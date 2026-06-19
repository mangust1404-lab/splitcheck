from decimal import Decimal

from pydantic import BaseModel


class ReceiptItem(BaseModel):
    name: str
    price: Decimal
    quantity: int = 1


class ReceiptScanResponse(BaseModel):
    items: list[ReceiptItem]
    total: Decimal | None = None
    tax: Decimal | None = None
    tips: Decimal | None = None
    currency: str | None = None
    raw_text: str | None = None
