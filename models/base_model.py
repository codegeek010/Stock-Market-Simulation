import uuid
from datetime import datetime
from typing import Optional, Dict
from fastapi import HTTPException, status
from sqlalchemy import Column, DateTime, Boolean, String
from sqlalchemy.orm import Session

from common.constants import INVALID_DATE_FORMAT
from database.db import Base


class BaseModel(Base):
    __abstract__ = True

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(
        DateTime, nullable=True, default=datetime.now, onupdate=datetime.now
    )
    is_active = Column(Boolean, nullable=False, default=True)


class BaseQueries:
    model: Optional = None

    @classmethod
    def get_record_with_id(cls, model_id: str, db: Session):
        return db.query(cls.model).filter(cls.model.id == model_id).first()

    @classmethod
    def get_record_with_(cls, db: Session, **kwargs):
        return db.query(cls.model).filter_by(**kwargs).first()

    @classmethod
    def get_all_record_with_(cls, db: Session, **kwargs):
        return db.query(cls.model).filter_by(**kwargs).all()

    @classmethod
    def get_all_records(cls, db: Session, limit=100, skip=0):
        return db.query(cls.model).offset(skip).limit(limit).all()

    @classmethod
    def create_record(cls, values: Dict, db: Session):
        obj = cls.model(**values)
        db.add(obj)
        db.flush()
        return obj

    @classmethod
    def update_record(cls, db: Session, record_id: str, update_data: Dict):
        return db.query(cls.model).filter(cls.model.id == record_id).update(update_data)

    @classmethod
    def get_records_by_timestamp_range(
        cls, db: Session, user_id: str, start_timestamp: str, end_timestamp: str
    ):
        try:
            start_datetime = datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S")
            end_datetime = datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S")

            transactions = (
                db.query(cls.model)
                .filter(
                    cls.model.user_id == user_id,
                    cls.model.timestamp >= start_datetime,
                    cls.model.timestamp <= end_datetime,
                )
                .all()
            )
            return transactions
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=INVALID_DATE_FORMAT,
            )
