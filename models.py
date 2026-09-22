from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    symbol: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    target_price: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    direction: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    is_triggered: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("false"),
        nullable=False
    )

    triggered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    notified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )