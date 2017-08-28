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

    def __init__(self, game, args=None):
        Sapiens.__init__(self, game, args)
        self.telepathy = Telepathy()

    def Step(self):
        self.sendMemory()
        self.receiveBytes()
        return Sapiens.Step(self)

    def Event(self, evt):
        Sapiens.Event(self, evt)

    def Path(self):
        return Sapiens.Path(self)

    def Victory(self):
        return Sapiens.Victory(self)

    def sendMemory(self):
        self.sendNewBytes(0xcc24, 0xcc35) # menu data

    def sendNewBytes(self, start, end):
        data = self.game.ReadBytesInRange(start, end) # menu data
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
                print("todo: write data")
                self.lastSent['offset'] = data
        except queue.Empty:
            pass

class Telepathy:
    inboundMemoryWrites = queue.Queue()
    outboundMemoryReads = queue.Queue()

    def __init__(self):
        thread = threading.Thread(target=self.threadMain, args=())
        thread.daemon = True
        thread.start()
        #asyncio.get_event_loop().run_forever()
    def threadMain(self):
        loop = asyncio.new_event_loop()
        #loop.run_in_executor(executor, self.handleSocket)
        loop.create_task(self.handleSocket())
        loop.run_forever()


    async def handleSocket(self):
        async with websockets.connect('ws://localhost:8765') as websocket:
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
            print("in messageproducer")

            #todo use a daemon thread
            message = await asyncio.get_event_loop().run_in_executor(None, self.bgThreadGetOutboundMemoryReads)

            print("sending a message: {}".format(message))
            pprint.pprint(message)
            await websocket.send(message)

    def bgThreadGetOutboundMemoryReads(self):
        return self.outboundMemoryReads.get()

LoadedBrain = Andalite
