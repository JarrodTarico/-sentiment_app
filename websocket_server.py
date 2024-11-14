import websockets, asyncio


async def handle_connection(websocket, path):
    print("New connection recieved")
    try:
        await websocket.send("Welcome to the Server")
        
        while True:
            message = await websocket.recv()
            print(f"Recieved message: {message}")
            await websocket.send(f"Server echo: {message}")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")

async def start_server():
    server = await websockets.serve(handle_connection, 'localhost', 8765)
    print("Server started at ws://localhost:8765")
    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(start_server())