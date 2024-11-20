import logging
from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from kafka import KafkaProducer
import praw, time, json


producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
analyzer = SentimentIntensityAnalyzer()
reddit = praw.Reddit(
    client_id =  "v2ldJgeXQ7arVGBkPHYGVQ",
    client_secret =  "yNFM5rvoCtVsahNwnH0iDHQOxLrElg",
    user_agent = "web:com.sentiment_analyzer:v1 (by u/WasabiApart1914)"
)
logger = logging.getLogger(__name__)

def text_analysis():
    res = []
    for submission in reddit.subreddit("stocks").hot(limit=25):
        timestamp = datetime.fromtimestamp(submission.created_utc)
        creation_date = timestamp.strftime( "%Y-%m-%dT%H:%M:%SZ")
        sentiment = analyzer.polarity_scores(submission.title)
        new_val = {
            "created_at": creation_date, 
            "title":  str(submission.title), 
            "num_comments": int(submission.num_comments),
            "upvotes": int(submission.score),
            "up_vote_to_down_vote_ratio": float(submission.upvote_ratio),
            "sentiment_score": sentiment
        }
        producer.send('reddit-posts', new_val)
    producer.flush()
    producer.close()
    return res

def run():
    logging.basicConfig(filename='myproducer.log', level=logging.INFO)
    text_analysis()

if __name__ == "__main__":
    run()
