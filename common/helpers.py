from typing import List

import redis

from config.config import settings
from models import StockData, Transaction
from schemas.transactions_schema import TransactionResponseSchema

consumer_config = {
    "bootstrap.servers": settings.KAFKA_BROKER,
    "group.id": "stock_data_consumer",
    "auto.offset.reset": "earliest",
}

redis_client = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)


def calculate_transaction_price(
    stock_data: StockData, transaction_type: str, transaction_volume: float
) -> float:
    """
    Calculate transaction price.

    Args:
        stock_data: StockData
        transaction_type: str
        transaction_volume: float

    Returns:
        Transaction Price
    """
    if transaction_type == "buy":
        return stock_data.low * transaction_volume

    return stock_data.high * transaction_volume


def jsonify_transactions_data(transactions: List[Transaction]):
    """
    Jsonify Transactions data.

    Args:
        transactions: List[Transaction]

    Returns:

    """
    validated_transactions_data = []
    for transaction in transactions:
        validated_data = TransactionResponseSchema(
            user_id=transaction.user_id,
            ticker=transaction.ticker,
            transaction_type=transaction.transaction_type,
            transaction_volume=transaction.transaction_volume,
            transaction_price=transaction.transaction_price,
            timestamp=transaction.timestamp,
        ).model_dump()
        validated_transactions_data.append(validated_data)

    return validated_transactions_data
