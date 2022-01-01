import json
from confluent_kafka import Producer
import random
import time
import sys
from os.path import abspath, join, dirname

sys.path.insert(0, abspath(join(dirname(__file__), "../..")))
from config.config import settings

topic = "stock_market_data"

producer_config = {
    "bootstrap.servers": settings.KAFKA_BROKER,
}

producer = Producer(producer_config)


def generate_stock_data(num_data_points: int):
    """
    Generate Stock data.

    Args:
        num_data_points: int

    """
    for _ in range(num_data_points):
        ticker = random.choice(["AAPL", "GOOGL", "MSFT", "AMZN"])
        open_price = round(random.uniform(100, 500), 2)
        close_price = round(random.uniform(100, 500), 2)
        high = max(open_price, close_price, round(random.uniform(100, 500), 2))
        low = min(open_price, close_price, round(random.uniform(100, 500), 2))
        volume = random.randint(1000, 1000000)
        timestamp = int(time.time() * 1000)

        data = {
            "ticker": ticker,
            "open_price": open_price,
            "close_price": close_price,
            "high": high,
            "low": low,
            "volume": volume,
            "timestamp": timestamp,
        }

        producer.produce(topic, key=ticker.encode(), value=json.dumps(data))
        producer.flush()

        print(f"Generated and sent data: {json.dumps(data)}")

        time.sleep(random.uniform(0.5, 2))


if __name__ == "__main__":
    total_num_data_points = 100
    generate_stock_data(total_num_data_points)
