from typing import Literal

from fastapi import APIRouter

from services.bybit import get_ticker


router = APIRouter(
    prefix="/coin",
    tags=["Market"]
)


@router.get("/{symbol}")
def get_coin(
    symbol: str,
    category: Literal["spot", "linear"] = "spot"
):
    return get_ticker(
        symbol=symbol,
        category=category
    )