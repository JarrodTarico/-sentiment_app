from kafka import KafkaProducer
from datetime import datetime
import json, random, time
import data_ingestion.utils.logger as logger

logger = logger.get_logger("dummy_producer")
producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
def run(delay=5):
    stock_counter = 0
    alphabet=list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    def on_send_success(record_metadata):
        logger.info(f"Message sent to {record_metadata.topic} partition {record_metadata.partition} at offset {record_metadata.offset}", extra={'app': 'dummy_producer'})

    def on_send_failure(exception):
        logger.error(f"Failed to send message: {exception}", extra={'app': 'dummy_producer'})

    while True:
        stock_ticker = f"{alphabet[random.randint(0,25)]}{alphabet[random.randint(0,25)]}{alphabet[random.randint(0,25)]}"
        stock_counter += 1
        total_upvotes = random.randint(0, 1000)
        total_comments = random.randint(0, 1000)
        avg_sentiment = round(random.uniform(-1, 1), 2)
        insertion_val = {
            "stock_ticker": stock_ticker,
            "total_upvotes": total_upvotes,
            "total_comments": total_comments,
            "avg_sentiment": avg_sentiment
        }
        try:
            producer.send(
                    "dummy-topic", insertion_val
                ).add_callback(on_send_success).add_errback(on_send_failure)            
            producer.send("dummy-topic", insertion_val)
        except Exception as e:
            logger.info(f"Failed to log dummy message {insertion_val['stock_ticker']}", extra={'app': 'dummy_producer'})
        time.sleep(delay)

if __name__ == "__main__":
    try:
        run(2)     
    except KeyboardInterrupt as e:
        print(f"{e}")
    finally:
        producer.flush()
        producer.close()        