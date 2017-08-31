import ast
import asyncio
import concurrent
import json
import pprint
import queue
import threading
import websockets

from sapiens import Sapiens
from sync import game_sync_classes

class Andalite(Sapiens):
    name = 'andalite'
    lastSent = {}

    def __init__(self, game, args=None, server='ws://localhost:8765'):
        Sapiens.__init__(self, game, args)
        self.telepathy = Telepathy(server)
        # get sync class for the currently loaded game.
        game_sync_class = game_sync_classes.get_game_sync_class(game.emu.gameinfo['name'])
        if game_sync_class is not None:
            self.game_sync = game_sync_class(self.game.PeekMemoryRegion, self.game.PokeMemoryRegion)

    def Step(self):
        if self.game_sync != None:
            self.sendData(self.game_sync.on_emulator_step(self.getReceivedData()))

        return Sapiens.Step(self)

    def getReceivedData(self):
        try:
            data = self.telepathy.inboundMemoryWrites.get_nowait()
            return data
        except queue.Empty:
            return []

    def sendData(self, data):
        if data:
            self.telepathy.outboundMemoryReads.put_nowait(str(data))

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
