from fastapi import APIRouter, Depends, HTTPException
from services.bybit import get_ticker
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Alert
from schemas import AlertCreate, AlertResponse, AlertUpdate


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)


# Получить все алерты
@router.get(
    "",
    response_model=list[AlertResponse]
)
def get_alerts(db: Session = Depends(get_db)):
    alerts = db.scalars(
        select(Alert)
    ).all()

    return alerts

@router.get("/check")
def check_alerts(db: Session = Depends(get_db)):
    alerts = db.scalars(
        select(Alert)
    ).all()

    results = []
    prices = {}

    for alert in alerts:
        symbol = alert.symbol.upper()

        # Если несколько алертов на одну монету,
        # цену Bybit запрашиваем только один раз
        if symbol not in prices:
            ticker = get_ticker(
                symbol=symbol,
                category="spot"
            )
            prices[symbol] = ticker["price"]

        current_price = prices[symbol]

        if alert.direction == "above":
            triggered = current_price >= alert.target_price
        else:
            triggered = current_price <= alert.target_price

        results.append({
            "id": alert.id,
            "symbol": alert.symbol,
            "target_price": alert.target_price,
            "current_price": current_price,
            "direction": alert.direction,
            "triggered": triggered,
            "created_at": alert.created_at
        })

    return results


# Создать алерт
@router.post(
    "",
    response_model=AlertResponse,
    status_code=201
)
def create_alert(
    alert: AlertCreate,
    db: Session = Depends(get_db)
):
    new_alert = Alert(
        symbol=alert.symbol.upper(),
        target_price=alert.target_price,
        direction=alert.direction
    )

    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)

    return new_alert


# Получить один алерт
@router.get(
    "/{alert_id}",
    response_model=AlertResponse
)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    alert = db.get(Alert, alert_id)

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail="Алерт не найден"
        )

    return alert


# Изменить алерт
@router.patch(
    "/{alert_id}",
    response_model=AlertResponse
)
def update_alert(
    alert_id: int,
    data: AlertUpdate,
    db: Session = Depends(get_db)
):
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


# Удалить алерт
@router.delete("/{alert_id}")
def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
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