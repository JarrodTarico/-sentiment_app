from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from kafka import KafkaConsumer
from threading import Thread
from cassandra.cluster import Cluster
# from confluent_kafka.admin import AdminClient
# from confluent_kafka import Consumer, TopicPartition
import data_ingestion.utils.logger as logger
import praw, time, json, asyncio, collections, logging

logger = logger.get_logger("dummy_consumer")
consumer = KafkaConsumer('dummy-topic',
                         bootstrap_servers='localhost:9092',
                         group_id='dummy-consumer-1',
                         auto_offset_reset='earliest', #if there is no offset avalible for the parition, this resets the offset to the beginning. 
                         value_deserializer=lambda x: json.loads(x.decode('utf-8')))

logging.basicConfig(level=logging.INFO)

# admin_client = AdminClient({'bootstrap.servers': 'localhost:9092'})
# metadata = admin_client.list_topics(timeout=10)
# topic_partitions = collections.defaultdict(list)
# for topic in metadata.topics.values():
#     print(f"Topic: {topic.topic}")
#     for partition in topic.partitions.values():
#         print(f"  Partition: {partition.id}, Leader: {partition.leader}")
#         topic_partitions[topic.topic].append(partition.id)

def save_to_db(data, data_type):
    """
    Store stock_data or metric_data in persistent store and timeseries database

    Args:
        data (list): A list that stores dictonaries of data to be stored in cassandra

    Returns:
        None. Saves data to cassandra and/or prometheus
    """
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()        
    print("here")
    if data_type not in set(['engagement', 'kafka_metrics', 'host_metrics']):
        raise ValueError('Data is not of right type, must be engagement, kafka, or metric data')
    if data_type == 'engagement':
        try:
            prepared = session.prepare("""
            INSERT INTO sentiment_data.dummy_engagement (stock_ticker, timestamp, total_comments, total_upvotes, avg_sentiment)
            VALUES (?, ?, ?, ?, ?)
            """)
            for event in data:  
                print(event.timestamp)
                print(type(event.value['stock_ticker']), event.value['stock_ticker'])
                session.execute(prepared, (
                    str(event.value['stock_ticker']), 
                    event.timestamp, 
                    int(event.value['total_comments']), 
                    int(event.value['total_upvotes']),
                    float(event.value['avg_sentiment']))
                )
            logger.info(f"Save {len(data)} engagement records to the db",  extra={'app': 'dummy_consumer', 'db_table':'engagement'})
        except Exception as e:
            logger.info(f"Failed to insert {len(data)} engagement records to the db with {e}",  extra={'app': 'dummy_consumer', 'db_table':'engagement'})
    elif data_type == 'kafka_metrics':
        pass
    else:
        pass

    session.shutdown()
    cluster.shutdown()    

def calculate_metrics(entity):
    if entity not in set('kafka', 'host'):
        raise ValueError('Data is not of right type, must be kafka or host data')

def consume_message_engagement(topic) -> None:
    """
    Consume messages from given topic

    Args:
        topic (str): The str value of the name of the topic

    Returns:
        None. Calls calulate_metrics and sends the engagement_date and metric_data to save_to_db
    """
    data = list()
    for message in consumer:
        data.append(message)
        if len(data) >= 5:
            save_to_db(data, 'engagement')
            data.clear()
    



def run(): 
    consume_message_engagement('dummy-topic')

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt as e:
        print(f"{e}")
        
    

# if __name__ == "__main__":
#     app.run(debug=True)
'''
    # Example consuming messages from the parition. Consumer is a generator and therefore can cause blocking. If no new data is avalible it blocks until a value is produced. 
    for message in consumer:
    print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,message.offset, message.key, message.value)) 
'''