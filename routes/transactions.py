from celery_service.tasks.save_transactions import save_transactions_data
from common.authentication import get_current_user
from common.constants import NO_DATA_FOUND, INSUFFICIENT_BALANCE
from common.helpers import calculate_transaction_price, jsonify_transactions_data
from database.db import get_db
from models.stocks import StockMethods
from models.transaction import TransactionMethods
import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import ORJSONResponse
from sqlalchemy.orm import Session


from models.user import User
from schemas.transactions_schema import TransactionRequestSchema

transactions_router = APIRouter(
    prefix="/transactions",
    responses={404: {"description": "Not found"}},
)


@transactions_router.post("/")
async def create_transaction(
    transaction: TransactionRequestSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ORJSONResponse:
    """
    Create Transactions.

    Args:
        transaction: TransactionRequestSchema
        current_user: User
        db: Session

    Returns:
        ORJSONResponse
    """
    stock_data = StockMethods.get_record_with_(db, ticker=transaction.ticker)
    if not stock_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NO_DATA_FOUND)

    transaction_price = calculate_transaction_price(
        stock_data, transaction.transaction_type, transaction.transaction_volume
    )

    if transaction.transaction_type == "buy":
        new_balance = current_user.balance - transaction_price
    else:
        new_balance = current_user.balance + transaction_price

    if new_balance < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=INSUFFICIENT_BALANCE
        )

    transaction_data = {
        "user_id": current_user.id,
        "ticker": transaction.ticker,
        "transaction_type": transaction.transaction_type,
        "transaction_volume": transaction.transaction_volume,
        "transaction_price": transaction_price,
        "timestamp": datetime.datetime.now(),
    }

    task_result = save_transactions_data.delay(transaction_data, new_balance)

    return ORJSONResponse(
        status_code=status.HTTP_200_OK, content={"task_id": task_result.id}
    )


@transactions_router.get("/{user_id}/")
async def get_user_transactions(
    user_id: str, db: Session = Depends(get_db)
) -> ORJSONResponse:
    """
    Get all transactions by user_id.

    Args:
        user_id: str
        db: Session

    Returns:
        ORJSONResponse
    """
    transactions = TransactionMethods.get_all_record_with_(db, user_id=user_id)

    if not transactions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NO_DATA_FOUND)

    transactions_data = jsonify_transactions_data(transactions)

    return ORJSONResponse(
        content={"data": transactions_data}, status_code=status.HTTP_200_OK
    )


@transactions_router.get("/{user_id}/{start_timestamp}/{end_timestamp}/")
async def get_user_transactions_by_timestamp(
    user_id: str,
    start_timestamp: str,
    end_timestamp: str,
    db: Session = Depends(get_db),
) -> ORJSONResponse:
    """
    Get user transaction by time duration.

    Args:
        user_id: str
        start_timestamp: Date
        end_timestamp: Date
        db: Session

    Returns:
        ORJSONResponse
    """
    transactions = TransactionMethods.get_records_by_timestamp_range(
        db,
        user_id=user_id,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
    )
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found")

    transactions_data = jsonify_transactions_data(transactions)

    return ORJSONResponse(
        content={"data": transactions_data}, status_code=status.HTTP_200_OK
    )
