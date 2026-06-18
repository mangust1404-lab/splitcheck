from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.user import Base


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))
    paid_by_id: Mapped[int] = mapped_column(ForeignKey("group_members.id"))
    title: Mapped[str] = mapped_column(String(300))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3))
    exchange_rate: Mapped[Decimal] = mapped_column(Numeric(12, 6), default=Decimal("1"))
    receipt_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    split_type: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    items: Mapped[list["ExpenseItem"]] = relationship(
        back_populates="expense", cascade="all, delete-orphan"
    )
    shares: Mapped[list["ExpenseShare"]] = relationship(
        back_populates="expense", cascade="all, delete-orphan"
    )


class ExpenseItem(Base):
    __tablename__ = "expense_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    expense_id: Mapped[int] = mapped_column(
        ForeignKey("expenses.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(300))
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    expense: Mapped["Expense"] = relationship(back_populates="items")


class ExpenseShare(Base):
    __tablename__ = "expense_shares"

    id: Mapped[int] = mapped_column(primary_key=True)
    expense_id: Mapped[int] = mapped_column(
        ForeignKey("expenses.id", ondelete="CASCADE")
    )
    member_id: Mapped[int] = mapped_column(ForeignKey("group_members.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    item_id: Mapped[int | None] = mapped_column(
        ForeignKey("expense_items.id", ondelete="SET NULL"), nullable=True
    )

    expense: Mapped["Expense"] = relationship(back_populates="shares")
