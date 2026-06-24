import logging
from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.deps import get_current_user
from app.models import Expense, ExpenseItem, ExpenseShare, Group, GroupMember, User
from app.schemas.expense import ExpenseCreate, ExpenseOut
from app.services.currency import get_exchange_rates

logger = logging.getLogger(__name__)

router = APIRouter(tags=["expenses"])


@router.get("/api/groups/{group_id}/expenses", response_model=list[ExpenseOut])
async def list_expenses(
    group_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _verify_membership(group_id, user.id, db)
    result = await db.execute(
        select(Expense)
        .where(Expense.group_id == group_id)
        .options(selectinload(Expense.items), selectinload(Expense.shares))
        .order_by(Expense.created_at.desc())
    )
    return result.scalars().all()


@router.post("/api/groups/{group_id}/expenses", response_model=ExpenseOut, status_code=201)
async def create_expense(
    group_id: int,
    body: ExpenseCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _verify_membership(group_id, user.id, db)

    # Auto-fetch exchange rate if expense currency differs from group base currency
    exchange_rate = body.exchange_rate
    group = await db.get(Group, group_id)
    if (
        group
        and body.currency.upper() != group.base_currency.upper()
        and exchange_rate == Decimal("1")
    ):
        try:
            rates = await get_exchange_rates(body.currency.upper())
            rate = rates.get(group.base_currency.upper())
            if rate:
                exchange_rate = Decimal(str(rate)).quantize(
                    Decimal("0.000001"), rounding=ROUND_HALF_UP
                )
                logger.info(
                    "Auto exchange rate %s→%s: %s",
                    body.currency, group.base_currency, exchange_rate,
                )
        except Exception as e:
            logger.warning("Failed to fetch exchange rate: %s", e)

    expense = Expense(
        group_id=group_id,
        paid_by_id=body.paid_by_id,
        title=body.title,
        total_amount=body.total_amount,
        currency=body.currency,
        exchange_rate=exchange_rate,
        receipt_image_url=body.receipt_image_url,
        split_type=body.split_type,
    )
    db.add(expense)
    await db.flush()

    if body.split_type == "equal" and body.split_among:
        share_amount = (body.total_amount / len(body.split_among)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        for member_id in body.split_among:
            share = ExpenseShare(
                expense_id=expense.id, member_id=member_id, amount=share_amount
            )
            db.add(share)

    elif body.split_type == "by_items" and body.items:
        for item_data in body.items:
            item = ExpenseItem(
                expense_id=expense.id,
                name=item_data.name,
                price=item_data.price,
                quantity=item_data.quantity,
            )
            db.add(item)
            await db.flush()

        if body.shares:
            for share_data in body.shares:
                share = ExpenseShare(
                    expense_id=expense.id,
                    member_id=share_data.member_id,
                    amount=share_data.amount,
                    item_id=share_data.item_id,
                )
                db.add(share)

    elif body.split_type == "custom" and body.shares:
        for share_data in body.shares:
            share = ExpenseShare(
                expense_id=expense.id,
                member_id=share_data.member_id,
                amount=share_data.amount,
            )
            db.add(share)

    await db.commit()

    result = await db.execute(
        select(Expense)
        .where(Expense.id == expense.id)
        .options(selectinload(Expense.items), selectinload(Expense.shares))
    )
    return result.scalar_one()


@router.get("/api/expenses/{expense_id}", response_model=ExpenseOut)
async def get_expense(
    expense_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Expense)
        .where(Expense.id == expense_id)
        .options(selectinload(Expense.items), selectinload(Expense.shares))
    )
    expense = result.scalar_one_or_none()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    await _verify_membership(expense.group_id, user.id, db)
    return expense


@router.delete("/api/expenses/{expense_id}", status_code=204)
async def delete_expense(
    expense_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    expense = result.scalar_one_or_none()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    await _verify_membership(expense.group_id, user.id, db)
    await db.delete(expense)
    await db.commit()


@router.patch("/api/expenses/{expense_id}", response_model=ExpenseOut)
async def update_expense(
    expense_id: int,
    body: ExpenseCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Expense)
        .where(Expense.id == expense_id)
        .options(selectinload(Expense.items), selectinload(Expense.shares))
    )
    expense = result.scalar_one_or_none()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    await _verify_membership(expense.group_id, user.id, db)

    # Update fields
    expense.title = body.title
    expense.total_amount = body.total_amount
    expense.currency = body.currency
    expense.exchange_rate = body.exchange_rate
    expense.paid_by_id = body.paid_by_id
    expense.split_type = body.split_type
    expense.receipt_image_url = body.receipt_image_url

    # Delete old items and shares
    for item in expense.items:
        await db.delete(item)
    for share in expense.shares:
        await db.delete(share)
    await db.flush()

    # Recreate items and shares (same logic as create)
    if body.split_type == "equal" and body.split_among:
        share_amount = (body.total_amount / len(body.split_among)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        for member_id in body.split_among:
            db.add(ExpenseShare(expense_id=expense.id, member_id=member_id, amount=share_amount))

    elif body.split_type == "by_items" and body.items:
        for item_data in body.items:
            item = ExpenseItem(
                expense_id=expense.id, name=item_data.name,
                price=item_data.price, quantity=item_data.quantity,
            )
            db.add(item)
            await db.flush()
        if body.shares:
            for share_data in body.shares:
                db.add(ExpenseShare(
                    expense_id=expense.id, member_id=share_data.member_id,
                    amount=share_data.amount, item_id=share_data.item_id,
                ))

    elif body.split_type == "custom" and body.shares:
        for share_data in body.shares:
            db.add(ExpenseShare(
                expense_id=expense.id, member_id=share_data.member_id,
                amount=share_data.amount,
            ))

    await db.commit()

    result = await db.execute(
        select(Expense).where(Expense.id == expense.id)
        .options(selectinload(Expense.items), selectinload(Expense.shares))
    )
    return result.scalar_one()


async def _verify_membership(group_id: int, user_id: int, db: AsyncSession):
    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id, GroupMember.user_id == user_id
        )
    )
    if result.scalar_one_or_none() is not None:
        return
    # Fallback: check if user is the group creator (for legacy groups)
    from app.models import Group as GroupModel
    group = await db.get(GroupModel, group_id)
    if group is None or group.created_by_id != user_id:
        raise HTTPException(status_code=403, detail="Not a member of this group")
