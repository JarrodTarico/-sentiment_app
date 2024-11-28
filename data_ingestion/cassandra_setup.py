from cassandra.cluster import Cluster
import data_ingestion.utils.logger as logger

logger.get_logger("cassandra_setup")

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
        session.execute(""""
            CREATE TABLE IF NOT EXISTS engagment(
                stock_ticker TEXT,
                timestamp TIMESTAMP,
                total_comments int,
                total_upvotes int,
                avg_sentiment float, 
                PRIMARY KEY((stock_ticker), timestamp, total_comments, total_upvotes))
            ) WITH CLUSTERING ORDER BY (timestamp DESC, total_comments DESC, total_upvotes DESC)
        """)
        logger.info(f"Successfully created engagment table")
    except Exception as e:
        logger.error(f"ERROR: failed to create table: {e}")
    
    session.shutdown()
    cluster.shutdown()
    

if __name__ == "__main__":
    setup_cassandra_schema()