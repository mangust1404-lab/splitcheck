from fastapi import APIRouter, Query

from app.services.currency import get_exchange_rates

router = APIRouter(prefix="/api/currencies", tags=["currencies"])


@router.get("/rates")
async def get_rates(base: str = Query("USD", max_length=3)):
    rates = await get_exchange_rates(base.upper())
    return {"base": base.upper(), "rates": rates}
