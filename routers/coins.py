from typing import Literal

import httpx
from fastapi import APIRouter, HTTPException


router = APIRouter(
    prefix="/coin",
    tags=["Market"]
)


@router.get("/{symbol}")
def get_coin(
    symbol: str,
    category: Literal["spot", "linear"] = "spot"
):
    coin = symbol.upper()
    pair = f"{coin}USDT"

    url = "https://api.bybit.kz/v5/market/tickers"

    params = {
        "category": category,
        "symbol": pair
    }

    try:
        response = httpx.get(
            url,
            params=params,
            timeout=5.0
        )

        response.raise_for_status()
        data = response.json()

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Bybit временно недоступен"
        )

    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail="Ошибка ответа от Bybit"
        )

    if data.get("retCode") != 0:
        raise HTTPException(
            status_code=404,
            detail=f"Монета {coin} не найдена"
        )

    tickers = data.get("result", {}).get("list", [])

    if not tickers:
        raise HTTPException(
            status_code=404,
            detail=f"Монета {coin} не найдена"
        )

    ticker = tickers[0]

    price = float(ticker["lastPrice"])
    change_24h = float(ticker["price24hPcnt"]) * 100
    high_24h = float(ticker["highPrice24h"])
    low_24h = float(ticker["lowPrice24h"])
    volume_24h = float(ticker["volume24h"])

    return {
        "symbol": coin,
        "pair": pair,
        "category": category,
        "price": price,
        "change_24h_percent": round(change_24h, 2),
        "high_24h": high_24h,
        "low_24h": low_24h,
        "volume_24h": round(volume_24h, 2)
    }