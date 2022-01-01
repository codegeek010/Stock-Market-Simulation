from pydantic import BaseModel


class StockDataSchema(BaseModel):
    ticker: str
    open_price: float
    close_price: float
    high: float
    low: float
    volume: int
    timestamp: int

    class Config:
        from_attributes = True


class StockDataResponseSchema(BaseModel):
    ticker: str
    open_price: float
    close_price: float
    high: float
    low: float
    volume: int
    timestamp: str

    class Config:
        from_attributes = True
