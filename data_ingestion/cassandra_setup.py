from cassandra.cluster import Cluster
import data_ingestion.utils.logger as logger

logger = logger.get_logger("cassandra_setup")

def setup_cassandra_schema():
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()
    try:
        session.execute( """
            CREATE KEYSPACE IF NOT EXISTS sentiment_data
            WITH replication = {'class':'SimpleStrategy', 'replication_factor':'1'};
        """)
        session.set_keyspace('sentiment_data')
        logger.info(f"Successfully created keyspace")
    except Exception as e:
        logger.error(f"ERROR: Failed to set up cassandra cluster: {e}")
    
    try:
        session.execute("""
            CREATE TABLE IF NOT EXISTS engagment (
                stock_ticker TEXT,
                timestamp TIMESTAMP,
                total_comments int,
                total_upvotes int,
                avg_sentiment float, 
                PRIMARY KEY ((stock_ticker), timestamp, total_comments, total_upvotes)
            ) WITH CLUSTERING ORDER BY (timestamp DESC, total_comments DESC, total_upvotes DESC);
        """)
        session.execute("""
            CREATE TABLE IF NOT EXISTS dummy_engagement (
                stock_ticker TEXT,
                timestamp TIMESTAMP,
                total_comments int,
                total_upvotes int,
                avg_sentiment float, 
                PRIMARY KEY ((stock_ticker), timestamp, total_comments, total_upvotes)
            ) WITH CLUSTERING ORDER BY (timestamp DESC, total_comments DESC, total_upvotes DESC);
        """)            
        logger.info(f"Successfully created engagement table")
        session.execute("""
            CREATE TABLE IF NOT EXISTS host_metrics (
                host_id TEXT,
                avg_cpu_usage float,
                avg_memory_usage float,
                disk_io_operations int,
                timestamp TIMESTAMP,
                PRIMARY KEY((host_id), timestamp)
            ) WITH CLUSTERING ORDER BY (timestamp DESC)
                AND default_time_to_live=3153600; --1-year ttl 
        """)
        logger.info(f"Successfully created host_metrics table")
        session.execute("""
            CREATE TABLE IF NOT EXISTS kafka_metrics (
                topic TEXT,
                partition INT, --kafka partition for more granular tracking
                produce_count int, --number of messages produced
                consume_count int, --number of messages consumed
                consumer_lag INT, --latest_produced_offset - last_consumed_offset
                disk_usage BIGINT, --Storage used by the topic/partition in MB or GB
                produce_latency FLOAT, --The time it takes for a producer to send a message to a partition and receive an acknowledgment from the broker
                consume_latency FLOAT, --The time it takes for a consumer to fetch a message from a parition after it has been written
                timestamp TIMESTAMP,
                PRIMARY KEY((topic, partition), timestamp)
            ) WITH CLUSTERING ORDER BY (timestamp DESC);
        """)                         
        logger.info(f"Successfully created kafka_metrics table")
    except Exception as e:
        logger.error(f"ERROR: failed to create tables: {e}")
        print(f"ERROR: failed to create tables: {e}")
    
    session.shutdown()
    cluster.shutdown()
    

if __name__ == "__main__":
    setup_cassandra_schema()