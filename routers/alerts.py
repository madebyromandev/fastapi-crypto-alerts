from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from database import SessionLocal
from models import Alert
from schemas import AlertCreate, AlertUpdate, AlertResponse


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)


@router.get(
    "",
    response_model=list[AlertResponse]
)
def get_alerts():
    with SessionLocal() as db:
        alerts = db.scalars(
            select(Alert)
        ).all()

        return alerts


@router.post(
    "",
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


@router.get(
    "/{alert_id}",
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


@router.patch(
    "/{alert_id}",
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


@router.delete("/{alert_id}")
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