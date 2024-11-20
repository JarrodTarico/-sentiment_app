from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from kafka import KafkaConsumer
from threading import Thread
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

def send_data_to_socket():
    for message in consumer:
        print(f"Recieved message of type {type(message.value)}")
        reduced_message = {
            "title": message.value.get("title"),
            "created_at": message.value.get("created_at"),
            "num_comments": message.value.get("num_comments"),
            "upvotes": message.value.get("upvotes")
        }
        test_data = {
                'title': 'Test Post',
                'created_at': '2024-11-18T10:46:08Z',
                'num_comments': 12,
                'upvotes': 123,
                'up_vote_to_down_vote_ratio': 0.9,
                'sentiment_score': {
                    'neg': 0.0,
                    'neu': 1.0,
                    'pos': 0.0,
                    'compound': 0.0
            }
        }       
        data = json.dumps(test_data)
        print(f"new message \n {data}")
        socketio.emit('new_message', data)

#Start to stream messages from to websocket clients
@socketio.on('start_stream')
def handle_stream():
    thread = Thread(target=send_data_to_socket)
    thread.start() #starts a seperate thread alongside our main thread to prevent blocking
    
    

if __name__ == "__main__":
    # app.run(debug=True)
    socketio.run(app, debug=True)
    '''
        # Example consuming messages from the parition. Consumer is a generator and therefore can cause blocking. If no new data is avalible it blocks until a value is produced. 
        for message in consumer:
         print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,message.offset, message.key, message.value)) 
    '''

async def websocket_client():
    uri = "ws://localhost:8765"  # WebSocket server URL
    
    async with websockets.connect(uri) as websocket:
        print("Connected to the server!")
        
        greeting = await websocket.recv()
        print(f"Received from server: {greeting}")
        
        await websocket.send("Hello, Server!")
        print("Sent message to server: Hello, Server!")
        
        response = await websocket.recv()
        print(f"Received from server: {response}")