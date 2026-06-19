from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.deps import get_current_user
from app.models import Expense, ExpenseItem, ExpenseShare, Group, GroupMember, User
from app.schemas.expense import ExpenseCreate, ExpenseOut

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

    expense = Expense(
        group_id=group_id,
        paid_by_id=body.paid_by_id,
        title=body.title,
        total_amount=body.total_amount,
        currency=body.currency,
        exchange_rate=body.exchange_rate,
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


async def _verify_membership(group_id: int, user_id: int, db: AsyncSession):
    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id, GroupMember.user_id == user_id
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=403, detail="Not a member of this group")
