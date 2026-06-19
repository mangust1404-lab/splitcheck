from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ExpenseItemCreate(BaseModel):
    name: str
    price: Decimal
    quantity: int = 1


class ShareCreate(BaseModel):
    member_id: int
    amount: Decimal
    item_id: int | None = None


class ExpenseCreate(BaseModel):
    title: str
    total_amount: Decimal
    currency: str
    exchange_rate: Decimal = Decimal("1")
    paid_by_id: int
    split_type: str  # equal, by_items, custom
    split_among: list[int] | None = None
    items: list[ExpenseItemCreate] | None = None
    shares: list[ShareCreate] | None = None
    receipt_image_url: str | None = None


class ExpenseItemOut(BaseModel):
    id: int
    name: str
    price: Decimal
    quantity: int

    model_config = {"from_attributes": True}


class ExpenseShareOut(BaseModel):
    id: int
    member_id: int
    amount: Decimal
    item_id: int | None

    model_config = {"from_attributes": True}


class ExpenseOut(BaseModel):
    id: int
    group_id: int
    paid_by_id: int
    title: str
    total_amount: Decimal
    currency: str
    exchange_rate: Decimal
    receipt_image_url: str | None
    split_type: str
    created_at: datetime
    items: list[ExpenseItemOut] = []
    shares: list[ExpenseShareOut] = []

    model_config = {"from_attributes": True}
