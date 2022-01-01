from sqlalchemy import Column, String, Float, BigInteger, DateTime
from .base_model import BaseModel, BaseQueries


class StockData(BaseModel):
    __tablename__ = "stock_data"

    ticker = Column(String, index=True)
    open_price = Column(Float)
    close_price = Column(Float)
    high = Column(Float)
    low = Column(Float)
    volume = Column(BigInteger)
    timestamp = Column(DateTime)


class StockMethods(BaseQueries):
    model = StockData
