from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base_model import BaseModel, BaseQueries


class Transaction(BaseModel):
    __tablename__ = "transactions"

    user_id = Column(String, ForeignKey("users.id"))
    ticker = Column(String, index=True)
    transaction_type = Column(String)
    transaction_volume = Column(Float)
    transaction_price = Column(Float)
    timestamp = Column(DateTime)

    user = relationship("User", back_populates="transactions")


class TransactionMethods(BaseQueries):
    model = Transaction
