from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.deps import get_current_user
from app.models import (
    Expense,
    ExpenseShare,
    Group,
    GroupMember,
    Settlement,
    User,
)
from app.schemas.settlement import BalanceOut, SettlementOut, SettlementUpdate
from app.services.settlement_calculator import calculate_balances, minimize_settlements

router = APIRouter(tags=["settlements"])


@router.get("/api/groups/{group_id}/balances", response_model=list[BalanceOut])
async def get_balances(
    group_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _verify_membership(group_id, user.id, db)

    expenses_data = await _load_expenses_for_calculation(group_id, db)
    balances = calculate_balances(expenses_data)

    members = await _load_members(group_id, db)

    result = []
    for member in members:
        result.append(
            BalanceOut(
                member_id=member.id,
                display_name=member.display_name,
                balance=balances.get(member.id, 0),
            )
        )
    return result


@router.get("/api/groups/{group_id}/settlements", response_model=list[SettlementOut])
async def get_settlements(
    group_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _verify_membership(group_id, user.id, db)

    expenses_data = await _load_expenses_for_calculation(group_id, db)
    balances = calculate_balances(expenses_data)
    optimal = minimize_settlements(balances)

    members = await _load_members(group_id, db)
    member_names = {m.id: m.display_name for m in members}

    group = await db.get(Group, group_id)

    # Delete old unsettled settlements and recreate
    await db.execute(
        delete(Settlement).where(
            Settlement.group_id == group_id, Settlement.is_settled == False
        )
    )

    # Load existing settled ones to preserve them
    result_settled = await db.execute(
        select(Settlement).where(
            Settlement.group_id == group_id, Settlement.is_settled == True
        )
    )
    settled = result_settled.scalars().all()

    # Create new unsettled settlements
    new_settlements = []
    for from_id, to_id, amount in optimal:
        s = Settlement(
            group_id=group_id,
            from_member_id=from_id,
            to_member_id=to_id,
            amount=amount,
            currency=group.base_currency,
        )
        db.add(s)
        new_settlements.append(s)

    await db.commit()

    all_settlements = list(settled) + new_settlements
    for s in all_settlements:
        await db.refresh(s)

    return [
        SettlementOut(
            id=s.id,
            from_member_id=s.from_member_id,
            from_member_name=member_names.get(s.from_member_id, "?"),
            to_member_id=s.to_member_id,
            to_member_name=member_names.get(s.to_member_id, "?"),
            amount=s.amount,
            currency=s.currency,
            is_settled=s.is_settled,
            settled_at=s.settled_at,
            confirmed_by_to=s.confirmed_by_to,
        )
        for s in all_settlements
    ]


@router.patch("/api/settlements/{settlement_id}", response_model=SettlementOut)
async def update_settlement(
    settlement_id: int,
    body: SettlementUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    settlement = await db.get(Settlement, settlement_id)
    if settlement is None:
        raise HTTPException(status_code=404, detail="Settlement not found")

    await _verify_membership(settlement.group_id, user.id, db)

    members = await _load_members(settlement.group_id, db)
    member_names = {m.id: m.display_name for m in members}

    if body.is_settled is not None:
        settlement.is_settled = body.is_settled
        settlement.settled_at = datetime.now(timezone.utc) if body.is_settled else None
    if body.confirmed_by_to is not None:
        settlement.confirmed_by_to = body.confirmed_by_to

    await db.commit()
    await db.refresh(settlement)

    return SettlementOut(
        id=settlement.id,
        from_member_id=settlement.from_member_id,
        from_member_name=member_names.get(settlement.from_member_id, "?"),
        to_member_id=settlement.to_member_id,
        to_member_name=member_names.get(settlement.to_member_id, "?"),
        amount=settlement.amount,
        currency=settlement.currency,
        is_settled=settlement.is_settled,
        settled_at=settlement.settled_at,
        confirmed_by_to=settlement.confirmed_by_to,
    )


async def _verify_membership(group_id: int, user_id: int, db: AsyncSession):
    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id, GroupMember.user_id == user_id
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=403, detail="Not a member")


async def _load_members(group_id: int, db: AsyncSession) -> list[GroupMember]:
    result = await db.execute(
        select(GroupMember).where(GroupMember.group_id == group_id)
    )
    return result.scalars().all()


async def _load_expenses_for_calculation(
    group_id: int, db: AsyncSession
) -> list[dict]:
    result = await db.execute(
        select(Expense)
        .where(Expense.group_id == group_id)
        .options(selectinload(Expense.shares))
    )
    expenses = result.scalars().all()

    return [
        {
            "paid_by_id": e.paid_by_id,
            "total_amount": e.total_amount,
            "exchange_rate": e.exchange_rate,
            "shares": [
                {"member_id": s.member_id, "amount": s.amount} for s in e.shares
            ],
        }
        for e in expenses
    ]
