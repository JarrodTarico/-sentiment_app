import scheduler
from twitter_ingestor import fetch_recent_tweets
from reddit_ingestor import fetch_subreddit_posts
from kafka_producer import send_to_kafka

def job():
    tweets = fetch_recent_tweets("Python", 10)
    for tweet in tweets:
        send_to_kafka("twitter_stream", tweet)

scheduler.every(10).minutes.do(job)