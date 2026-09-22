from typing import Literal
from datetime import datetime
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
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AlertCheckResponse(BaseModel):
    id: int
    symbol: str
    target_price: float
    current_price: float
    direction: str
    triggered: bool
    created_at: datetime
    triggered_at: datetime | None