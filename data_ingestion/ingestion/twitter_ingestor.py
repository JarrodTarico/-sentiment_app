import tweepy
from data_ingestion.config.twitter_config import TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_API_BASE_URL, TWITTER_ACCESS_TOKEN_SECRET

auth = tweepy.OAuth1UserHandler(TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAALRpxAEAAAAA%2BGk1vwK0BEZLy9Xqzewa0EWFhM4%3Dx2R5LEqnE223wZwmoqu7TPx2GURTZ4WsH2P6MtchTEKWDO4Gz7"

client = tweepy.Client(bearer_token=BEARER_TOKEN)

api = tweepy.API(auth)


def fetch_recent_tweets(count=10):
    public_tweets = api.home_timeline(count=count)
    for tweet in public_tweets:
        print(tweet.text)
    
    # response = client.search_recent_tweets(query="Python", max_results=count)
    # for tweet in response.data:
    #     print(tweet.text)    

if __name__ == "__main__":
    fetch_recent_tweets()