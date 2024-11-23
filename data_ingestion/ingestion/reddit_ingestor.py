from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from kafka import KafkaProducer
from data_ingestion.config.reddit_config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET
from logstash_async.handler import AsynchronousLogstashHandler
from logstash_async.formatter import LogstashFormatter
from logstash_async.transport import TcpTransport
import praw, time, json, collections, logging



producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
vader_sentiment = SentimentIntensityAnalyzer()


logstash_handler = AsynchronousLogstashHandler(
    host='192.168.1.166',
    port=5100,
    database_path='./logstash.db',
    ssl_enable=False,
    ssl_verify=False,
    transport=TcpTransport,
    transport_options={'timeout': 60}
)

logstash_handler.setFormatter(LogstashFormatter())
logger = logging.getLogger('logstash')
logger.addHandler(logstash_handler)

reddit = praw.Reddit(
    client_id =  REDDIT_CLIENT_ID,
    client_secret =  REDDIT_CLIENT_SECRET,
    user_agent = "web:com.sentiment_analyzer:v1 (by u/WasabiApart1914)"
)


subreddits = ["stocks", "investing", "wallstreetbets"]
stock_queries = ["AAPL OR Apple", "CRM OR Salesforce", "AMZN OR Amazon"]


def stream_to_producer(stock_data):
    try:
        producer.send("reddit-posts", stock_data)
        producer.flush()
        producer.close()
        logger.info(f"Successfully stream data for stock: {stock_data['stock_ticker']}", extra={'app': 'RedditIngestor'})
    except Exception as e:
        logger.error(f"Failed to stream data for stock: {stock_data['stock_ticker']}, ERROR: {e}", extra={'app': 'RedditIngestor'})


def calc_sentiment_engagement(stocks) -> None:
    """
    Calculate sentiment and engagement metrics for each stock's submissions.

    Args:
        stocks (dict): A dictionary where keys are stock tickers and values are lists of submission dictionaries.

    Returns:
        None. Sends aggregated metrics to Kafka.
    """    
    for stock, submissions in stocks.items():
        # Case: No data from reddit search
        if not submissions:
            logger.warning(f"No submissions for stock: {stock}", extra={'app': 'RedditIngestor'})
            continue
        total_comments = 0
        avg_sentiment = 0
        total_upvotes = 0
        for submission in submissions:
            total_comments += submission["num_comments"]
            sentiment_obj = vader_sentiment.polarity_scores(submission["title_body"])
            avg_sentiment += sentiment_obj["compound"]
            total_upvotes += submission["upvotes"]
        avg_sentiment = (avg_sentiment) / len(submission)
        insertion_val = {
            "stock_ticker": stock,
            "upvotes": total_upvotes,
            "num_comments": total_comments,
            "avg_sentiment": avg_sentiment
        }
        logger.info(f"Calculated {total_upvotes} total upvotes for stock: {stock}",  extra={'app': 'RedditIngestor','total_upvotes': total_upvotes})
        logger.info(f"Calculated {total_comments} total comments for stock: {stock}", extra={'app': 'RedditIngestor','total_comments': total_comments})
        logger.info(f"Calculated {avg_sentiment} average sentiment for stock: {stock}", extra={'app': 'RedditIngestor','avg_sentiment': avg_sentiment})
        stream_to_producer(insertion_val)


def text_analysis() -> None:
    stock_information = collections.defaultdict(list)
    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        for query in stock_queries:
            logger.info(f"Searching in subreddit: {subreddit_name} with query: {query}", extra={'app': 'RedditIngestor'})
            results = subreddit.search(query=query, limit=1)
            stock_ticker, i = "", 0
            while i < len(query) and query[i].isalpha():
                stock_ticker += query[i]
                i += 1
            for submission in results:
                curr_submission = {
                    "subreddit": subreddit_name,
                    "title": submission.title,
                    "url": submission.url,
                    "body": submission.selftext,
                    "num_comments": int(submission.num_comments),
                    "upvotes": int(submission.score),
                    "title_body": f"{submission.title} \n {submission.selftext}"                   
                }
                stock_information[stock_ticker].append(curr_submission)
    
    logger.info(f"Processed {len(stock_information)} stock tickers.", extra={'app': 'RedditIngestor'})
    calc_sentiment_engagement(stock_information)
    return


def run():
    logging.basicConfig(filename='logs/reddit_ingestion.log', level=logging.INFO)
    text_analysis()

if __name__ == "__main__":
    run()
