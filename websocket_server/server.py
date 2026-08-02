import websockets
import asyncio
from collections import defaultdict
import json



PORT = 8001
print("Server started!!!")

connected = defaultdict(set)


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
    server = await websockets.serve(echo, "localhost", PORT)
    print(f"WebSocket server listening on ws://localhost:{PORT}")

    # Keep the main coroutine running to keep the server alive
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
