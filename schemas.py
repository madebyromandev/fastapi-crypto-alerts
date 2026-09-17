from typing import Literal

from pydantic import BaseModel, ConfigDict, PositiveFloat


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