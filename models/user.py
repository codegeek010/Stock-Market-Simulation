from sqlalchemy import Column, String, Float
from sqlalchemy.orm import relationship
from .base_model import BaseModel, BaseQueries


class User(BaseModel):
    __tablename__ = "users"

    username = Column(String, unique=True, index=True)
    password = Column(String)
    balance = Column(Float, default=0.0)

    transactions = relationship("Transaction", back_populates="user")


class UserMethods(BaseQueries):
    model = User
