from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from kafka import KafkaConsumer
from threading import Thread
import collections
import logging
import producer
import praw, time, json, websockets, asyncio

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
logger = logging.getLogger(__name__)

consumer = KafkaConsumer('reddit-posts',
                         bootstrap_servers=['localhost:9092'],
                         group_id='flask-group',
                         auto_offset_reset='earliest', #if there is no offset avalible for the parition, this resets the offset to the beginning. 
                         value_deserializer=lambda x: json.loads(x.decode('utf-8')))

logging.basicConfig(level=logging.INFO)


# WEBSOCKET: bidirectional connection with the client and server
@app.route('/')
def index_websocket():
    return render_template('index_websocket.html')

# HTTP Long Polling unidirectional and client has to make a request each time they want new data from the queue. 
@app.route('/non_websocket')
def index_non_websocket():
    messages = []
    # NON WEBSOCKET: API call to get latest data from the stream and process in a non-blocking manner
    for _ in range(3):
        message = next(consumer) # because consumer is a generator
        app.logger.info(f'Reading {message}')
        messages.append(message.value)
    
    data = {
        'title': "Reddit Posts",
        'items': messages
    }
    return render_template('index.html', data=data)
    
@socketio.on('connect')
def handle_connect():
    logger.info("Client Connected")

@socketio.on('disconnect')
def handle_disconnect():
    logger.info("Client disconnected")

# message Queue for decoupling
message_queue = collections.deque()
def decouple_engine():
    for _ in range(len(list(consumer))):
        message = next(consumer)
        message_queue.append(message.value)


#Start to stream messages from to websocket clients
@socketio.on('start_stream')
def handle_stream():
    def send_data_to_socket():
        if len(message_queue) >= 2:
            data = []
            while message_queue:
                data.append(message_queue.popleft())
            socketio.emit('new_message', data)
        print(f"emitted a batch of size: 2")
    Thread(target=decouple_engine, daemon=True).start()
    socketio.start_background_task(send_data_to_socket)
    
    

if __name__ == "__main__":
    # app.run(debug=True)
     socketio.run(app, host="127.0.0.1", port=5000, debug=True)
'''
    # Example consuming messages from the parition. Consumer is a generator and therefore can cause blocking. If no new data is avalible it blocks until a value is produced. 
    for message in consumer:
    print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,message.offset, message.key, message.value)) 
'''