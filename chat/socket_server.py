import websockets
import asyncio
from collections import defaultdict
import json
import sys



PORT = 8001
DEFAULT_HOST = "localhost"
print("Server started!!!")

connected = defaultdict(set)

origins = ["http://localhost:8000"]


async def echo(websocket, path):
    print("Client Connected")
    connected[path].add(websocket)

    try:
        async for message in websocket:

            print(message)

            for webs in connected[path]:
                if webs != websocket:
                    await webs.send(message)
        
        connected[path].remove(websocket)
        print("Client Disconnected")

    except websockets.exceptions.ConnectionClosed as e:
        print("A Client disconnected", e)


async def main():
    host = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HOST
    server = await websockets.serve(echo, host, PORT)
    print(f"WebSocket server listening on ws://localhost:{PORT}")

    # Keep the main coroutine running to keep the server alive
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())