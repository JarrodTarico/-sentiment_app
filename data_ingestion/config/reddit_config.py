from dotenv import load_dotenv
import os, tweepy

load_dotenv()

REDDIT_CLIENT_ID=os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET=os.getenv("REDDIT_CLIENT_SECRET")