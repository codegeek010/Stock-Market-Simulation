import datetime
import json
from confluent_kafka import Consumer
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import ORJSONResponse
from sqlalchemy.orm import Session

from common.constants import (
    NO_DATA_FOUND,
    DATA_SAVED_SUCCESSFULLY,
)
from common.helpers import consumer_config, redis_client
from database.db import get_db
from logging_app import logger
from models.stocks import StockMethods, StockData
from schemas.stocks_schema import StockDataSchema, StockDataResponseSchema

stocks_router = APIRouter(
    prefix="/stocks",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@stocks_router.post("/create")
async def ingest_data_from_kafka(db: Session = Depends(get_db)) -> ORJSONResponse:
    """
    Ingest data in DB from Kafka topic.

    Args:
        db: Session

    Returns:
        ORJSONResponse
    """
    consumer = Consumer(consumer_config)

    consumer.subscribe(["stock_market_data"])

    try:
        while True:
            msg = consumer.poll(1.0)
            if not msg:
                break
            if msg.error():
                logger.error("Consumer error: %s", msg.error())
            else:
                try:
                    data = json.loads(msg.value().decode("utf-8"))
                    stock_data = StockDataSchema(**data).model_dump()
                    ticker = stock_data.get("ticker")

                    existing_data = StockMethods.get_record_with_(db, ticker=ticker)
                    if existing_data:
                        logger.info("Data for %s already exists, skipping...", ticker)
                        continue

                    timestamp = datetime.datetime.fromtimestamp(
                        data.get("timestamp") / 1000
                    )
                    stock_data["timestamp"] = timestamp
                    stocks_data = StockMethods.create_record(stock_data, db)
                    logger.info("Stock data saved: %s", stocks_data)
                except Exception as e:
                    logger.exception("Error processing Kafka message: %s", e)
    finally:
        db.commit()
        consumer.close()

    return ORJSONResponse(
        content={"message": DATA_SAVED_SUCCESSFULLY},
        status_code=status.HTTP_201_CREATED,
    )


@stocks_router.get("/")
async def get_all_stock_data(db: Session = Depends(get_db)) -> ORJSONResponse:
    """
    Retrieve all stock data.

    Args:
        db: Session

    Returns:
        List of StockData
    """
    cached_data = redis_client.get("all_stocks")
    if cached_data:
        return json.loads(cached_data)

    stocks_data = StockMethods.get_all_records(db)
    if not stocks_data:
        raise HTTPException(detail=NO_DATA_FOUND, status_code=status.HTTP_404_NOT_FOUND)

    validated_stocks_data = []
    for stock_data in stocks_data:
        validated_data = StockDataResponseSchema(
            ticker=stock_data.ticker,
            open_price=stock_data.open_price,
            close_price=stock_data.close_price,
            high=stock_data.high,
            low=stock_data.low,
            volume=stock_data.volume,
            timestamp=stock_data.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        ).model_dump()
        validated_stocks_data.append(validated_data)

    redis_client.set("all_stocks", json.dumps(validated_stocks_data), ex=3600)

    return ORJSONResponse(
        content={"data": validated_stocks_data}, status_code=status.HTTP_200_OK
    )


@stocks_router.get("/{ticker}")
async def get_specific_stock_data(
    ticker: str, db: Session = Depends(get_db)
) -> ORJSONResponse:
    """
    Retrieve specific stock data by ticker.

    Args:
        ticker: Ticker
        db: Session

    Returns:
        ORJSONResponse
    """
    cached_data = redis_client.get(ticker)
    if cached_data:
        return StockData(**json.loads(cached_data))

    stock_data = StockMethods.get_record_with_(db, ticker=ticker)
    if not stock_data:
        raise HTTPException(detail=NO_DATA_FOUND, status_code=status.HTTP_404_NOT_FOUND)

    stock_response_schema = StockDataResponseSchema(
        ticker=stock_data.ticker,
        open_price=stock_data.open_price,
        close_price=stock_data.close_price,
        high=stock_data.high,
        low=stock_data.low,
        volume=stock_data.volume,
        timestamp=stock_data.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
    ).model_dump()

    redis_client.set(ticker, json.dumps(stock_response_schema), ex=3600)

    return ORJSONResponse(
        content={"data": stock_response_schema}, status_code=status.HTTP_200_OK
    )
