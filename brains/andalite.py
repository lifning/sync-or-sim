import ast
import asyncio
import concurrent
import json
import pprint
import queue
import threading
import websockets

from sapiens import Sapiens

class Andalite(Sapiens):
    name = 'andalite'
    lastSent = {}

    def __init__(self, game, args=None, server='ws://localhost:8765'):
        Sapiens.__init__(self, game, args)
        self.telepathy = Telepathy(server)

    def Step(self):
        self.sendMemory()
        self.receiveBytes()
        return Sapiens.Step(self)

    def sendMemory(self):
        self.sendNewBytes(0xd009, 0x27) # menu data

    def sendNewBytes(self, start, lengthBytes):
        data = {'offset': start, 'data': self.game.PeekMemoryRegion(start, lengthBytes)} # menu data
        lastSentData = self.lastSent.get(start)
        if lastSentData != data:
            self.telepathy.outboundMemoryReads.put_nowait(str(data))
            self.lastSent[start] = data

    def receiveBytes(self):
        try:
            data = self.telepathy.inboundMemoryWrites.get_nowait()
            start = data.get('offset')
            lastData = self.lastSent.get(start)

            if lastData == None or start != None and lastData.get('data') != data.get('data'):
                print("writing data")
                self.game.PokeMemoryRegion(data['offset'], data['data'])
                self.lastSent[start] = data
        except queue.Empty:
            pass

class Telepathy:
    inboundMemoryWrites = queue.Queue()
    outboundMemoryReads = queue.Queue()

    def __init__(self, server):
        self.server = server
        thread = threading.Thread(target=self.threadMain, args=())
        thread.daemon = True
        thread.start()

    def threadMain(self):
        loop = asyncio.new_event_loop()
        loop.create_task(self.handleSocket())
        loop.run_forever()

    async def handleSocket(self):
        async with websockets.connect(self.server) as websocket:
            print("connected to websocket")
            consumerTask = asyncio.ensure_future(self.messageConsumer(websocket))
            producerTask = asyncio.ensure_future(self.messageProducer(websocket))
            done, pending = await asyncio.wait(
                    [consumerTask, producerTask],
                    return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                task.cancel()

    async def messageConsumer(self, websocket):
        while True:
            message = await websocket.recv()
            data = ast.literal_eval(message)
            print("received data:")
            pprint.pprint(data)
            self.inboundMemoryWrites.put_nowait(data)

    async def messageProducer(self, websocket):
        while True:
            try:
                message = await asyncio.get_event_loop().run_in_executor(None, self.bgThreadGetOutboundMemoryReads)
                print("sending a message: {}".format(message))
                pprint.pprint(message)
                await websocket.send(message)
            except queue.Empty:
                pass

    def bgThreadGetOutboundMemoryReads(self):
        timeoutSeconds = 3 # wait at most this many seconds, then call .get again
        # if we do not timeout here then the app will hang indefinitely when interrupted.
        return self.outboundMemoryReads.get(block=True, timeout=timeoutSeconds)

LoadedBrain = Andalite
