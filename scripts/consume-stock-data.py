from confluent_kafka import Consumer, KafkaError

from config.config import settings

topic = "stock_market_data"

consumer_config = {
    "bootstrap.servers": settings.KAFKA_BROKER,
    "group.id": "my-consumer-group",
    "auto.offset.reset": "earliest",
}

consumer = Consumer(consumer_config)

consumer.subscribe([topic])

try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
        else:
            print(f"Received message: {msg.value().decode('utf-8')}")

except KeyboardInterrupt:
    pass

finally:
    consumer.close()
