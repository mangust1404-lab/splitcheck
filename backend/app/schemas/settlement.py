from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class BalanceOut(BaseModel):
    member_id: int
    display_name: str
    balance: Decimal  # positive = owed to them, negative = they owe


class SettlementOut(BaseModel):
    id: int
    from_member_id: int
    from_member_name: str
    to_member_id: int
    to_member_name: str
    amount: Decimal
    currency: str
    is_settled: bool
    settled_at: datetime | None
    confirmed_by_to: bool

    model_config = {"from_attributes": True}


class SettlementUpdate(BaseModel):
    is_settled: bool | None = None
    confirmed_by_to: bool | None = None
