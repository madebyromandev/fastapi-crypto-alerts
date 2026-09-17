from typing import Literal

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, PositiveFloat
from sqlalchemy import select

from database import SessionLocal
from models import Alert


app = FastAPI(
    title="Crypto Alerts API",
    version="1.0.0"
)


# =========================
# Pydantic-модели
# =========================

class AlertCreate(BaseModel):
    symbol: str
    target_price: PositiveFloat
    direction: Literal["above", "below"]


class AlertUpdate(BaseModel):
    target_price: PositiveFloat | None = None
    direction: Literal["above", "below"] | None = None


class AlertResponse(BaseModel):
    id: int
    symbol: str
    target_price: float
    direction: str

    model_config = ConfigDict(from_attributes=True)


# =========================
# Главная страница
# =========================

@app.get("/")
def root():
    return {
        "message": "FastAPI работает!"
    }


# =========================
# Данные монеты с Bybit
# =========================

@app.get("/coin/{symbol}")
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


# =========================
# GET — получить все алерты
# =========================

@app.get(
    "/alerts",
    response_model=list[AlertResponse]
)
def get_alerts():
    with SessionLocal() as db:
        alerts = db.scalars(
            select(Alert)
        ).all()

        return alerts


# =========================
# POST — создать алерт
# =========================

@app.post(
    "/alerts",
    response_model=AlertResponse,
    status_code=201
)
def create_alert(alert: AlertCreate):
    with SessionLocal() as db:
        new_alert = Alert(
            symbol=alert.symbol.upper(),
            target_price=alert.target_price,
            direction=alert.direction
        )

        db.add(new_alert)
        db.commit()
        db.refresh(new_alert)

        return new_alert


# =========================
# GET — получить алерт по ID
# =========================

@app.get(
    "/alerts/{alert_id}",
    response_model=AlertResponse
)
def get_alert(alert_id: int):
    with SessionLocal() as db:
        alert = db.get(Alert, alert_id)

        if alert is None:
            raise HTTPException(
                status_code=404,
                detail="Алерт не найден"
            )

        return alert


# =========================
# PATCH — изменить алерт
# =========================

@app.patch(
    "/alerts/{alert_id}",
    response_model=AlertResponse
)
def update_alert(
    alert_id: int,
    data: AlertUpdate
):
    with SessionLocal() as db:
        alert = db.get(Alert, alert_id)

        if alert is None:
            raise HTTPException(
                status_code=404,
                detail="Алерт не найден"
            )

        if data.target_price is not None:
            alert.target_price = data.target_price

        if data.direction is not None:
            alert.direction = data.direction

        db.commit()
        db.refresh(alert)

        return alert


# =========================
# DELETE — удалить алерт
# =========================

@app.delete("/alerts/{alert_id}")
def delete_alert(alert_id: int):
    with SessionLocal() as db:
        alert = db.get(Alert, alert_id)

        if alert is None:
            raise HTTPException(
                status_code=404,
                detail="Алерт не найден"
            )

        db.delete(alert)
        db.commit()

        return {
            "message": "Алерт удалён",
            "id": alert_id
        }