from typing import Dict

from celery_service.celery import celery_app
from database.db import get_db
from models.transaction import TransactionMethods
from models.user import UserMethods


@celery_app.task
def save_transactions_data(transaction_data: Dict, new_balance: float):
    """
    Save Transactions data.

    Args:
        transaction_data: Dict
        new_balance: Float

    """

    db = next(get_db())
    TransactionMethods.create_record(transaction_data, db)
    UserMethods.update_record(db, transaction_data["user_id"], {"balance": new_balance})
    db.commit()
