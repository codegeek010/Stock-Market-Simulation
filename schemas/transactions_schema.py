from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class TransactionRequestSchema(BaseModel):
    ticker: str
    transaction_type: Literal["sell", "buy"]
    transaction_volume: float

    class Config:
        from_attributes = True


class TransactionResponseSchema(BaseModel):
    user_id: str
    ticker: str
    transaction_type: str
    transaction_volume: float
    transaction_price: float
    timestamp: datetime

    class Config:
        from_attributes = True
