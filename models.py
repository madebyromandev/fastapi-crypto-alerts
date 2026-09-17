from sqlalchemy import Float, Integer, String
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