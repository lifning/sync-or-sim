#!/usr/bin/env python

import asyncio
import threading
import time
import signal
import sys
import websockets

clients = set()

async def handleClient(websocket, path):
    global connected
    clients.add(websocket)

    try:
        while True:
            message = await websocket.recv()
            print("< {}".format(message))

            await broadcastMessage(websocket, message)
            print("sent {}".format(message))
    finally:
        clients.remove(websocket)

async def broadcastMessage(origin, message):
    destinations = clients - set([origin])
    messagesSent = 0
    for dest in destinations:
        await dest.send(message)
        messagesSent = messagesSent + 1
    print ("Sent message {} times: {}".format(messagesSent, message))

def websocketServer():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(handleClient, 'localhost', 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

thread = threading.Thread(target=websocketServer, args=())
thread.daemon = True
thread.start()

def signal_handler(signal, frame):
    print("\nStopping server.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

while True:
    time.sleep(20)
