from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from kafka import KafkaConsumer
import praw, time, json, websockets, asyncio

app = Flask(__name__)

consumer = KafkaConsumer('reddit-posts',
                         bootstrap_servers=['localhost:9092'],
                         group_id='my_consumer_group',
                         value_deserializer=lambda x: json.loads(x.decode('utf-8')))

@app.route('/')
def index():
    data = []
    for message in consumer:
        print(message.value)
        data.append(message.value)
    return render_template('index.html', data=data)

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








if __name__ == "__main__":
    # asyncio.run(websocket_client())
    # app.run(debug=True)
    print("here")
    for message in consumer:
        print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,message.offset, message.key, message.value)) 