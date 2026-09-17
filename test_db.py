from sqlalchemy import select

from database import SessionLocal
from models import Alert


with SessionLocal() as db:
    alerts = db.scalars(
        select(Alert)
    ).all()

    for alert in alerts:
        print(
            alert.id,
            alert.symbol,
            alert.target_price,
            alert.direction
        )