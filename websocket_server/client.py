import websockets
import asyncio

async def listen():
    url = "ws://127.0.0.1:8001/"

    async with websockets.connect(url) as ws:
        while True:
            to_send = input("Enter: ")
            
            await ws.send(to_send)

            await ws.recv()
            # print("rceived something")
        
            # send_task = asyncio.create_task(ws.send(to_send))


asyncio.get_event_loop().run_until_complete(listen())
