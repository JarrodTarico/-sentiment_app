from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from kafka import KafkaProducer
from data_ingestion.config.reddit_config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET
import praw, time, json, collections, logging

producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
analyzer = SentimentIntensityAnalyzer()
reddit = praw.Reddit(
    client_id =  REDDIT_CLIENT_ID,
    client_secret =  REDDIT_CLIENT_SECRET,
    user_agent = "web:com.sentiment_analyzer:v1 (by u/WasabiApart1914)"
)

logger = logging.getLogger(__name__)

subreddits = ["stocks", "investing", "wallstreetbets"]
stock_queries = ["AAPL OR Apple", "CRM OR Salesforce", "AMZN OR Amazon"]

def calc_sentiment(stocks):
    # also calculate the total num of comments
    pass

def stream_to_producer(stocks):
    pass

def text_analysis():
    stock_information = collections.defaultdict(list)
    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        for query in stock_queries:
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
                }
                stock_information[stock_ticker].append(curr_submission)                      
    producer.flush()
    producer.close()
    # return res

def run():
    logging.basicConfig(filename='logs/reddit_injestion.log', level=logging.INFO)
    text_analysis()

if __name__ == "__main__":
    run()
