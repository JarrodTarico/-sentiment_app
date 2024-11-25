from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from kafka import KafkaConsumer
from threading import Thread
import collections
import logging
import praw, time, json, websockets, asyncio

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
logger = logging.getLogger(__name__)

consumer = KafkaConsumer('reddit-posts',
                         bootstrap_servers=['localhost:9092'],
                         group_id='reddit-consumer-1',
                         auto_offset_reset='earliest', #if there is no offset avalible for the parition, this resets the offset to the beginning. 
                         value_deserializer=lambda x: json.loads(x.decode('utf-8')))

logging.basicConfig(level=logging.INFO)

 
@app.route('/')
def index_non_websocket():
    messages = []
    for _ in range(3):
        message = next(consumer) # because consumer is a generator
        app.logger.info(f'Reading {message}')
        messages.append(message.value)
    
    data = {
        'title': "Reddit Posts",
        'items': messages
    }
    return render_template('index.html', data=data)
        
    

if __name__ == "__main__":
    app.run(debug=True)
'''
    # Example consuming messages from the parition. Consumer is a generator and therefore can cause blocking. If no new data is avalible it blocks until a value is produced. 
    for message in consumer:
    print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,message.offset, message.key, message.value)) 
'''