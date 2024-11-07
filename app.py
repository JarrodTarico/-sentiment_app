from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import praw

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
analyzer = SentimentIntensityAnalyzer()
reddit = praw.Reddit(
    client_id =  "v2ldJgeXQ7arVGBkPHYGVQ",
    client_secret =  "yNFM5rvoCtVsahNwnH0iDHQOxLrElg",
    user_agent = "web:com.sentiment_analyzer:v1 (by u/WasabiApart1914)"
)


sentences = ["Hello world its tony",  # positive sentence example
             "That's not funny",  # punctuation emphasis handled correctly (sentiment intensity adjusted)
             "Hello and welcome", # booster words handled correctly (sentiment intensity adjusted)
             "Jarrod is VERY SMART, handsome, and FUNNY.", ]  # emphasis for ALLCAPS handled

def text_analysis():
    res = []
    for submission in reddit.subreddit("stocks").hot(limit=10):
        timestamp = datetime.fromtimestamp(submission.created_utc)
        creation_date = timestamp.strftime( "%Y-%m-%dT%H:%M:%SZ")
        context = f'created_at ", {creation_date}, "title ", {submission.title}, "num_comments ", {submission.num_comments}, "upvotes", {submission.score}, "ratio ", {submission.upvote_ratio}'
        val = analyzer.polarity_scores(submission.title)
        str1 = "{:-<65} {} {}".format(submission.title, str(val), context)
        res.append(str1)
    return res

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    with app.app_context():
        db.create_all()

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/')
def index():
    return text_analysis()
    # return render_template('index.html')



if __name__ == "__main__":
    app.run(debug=True)