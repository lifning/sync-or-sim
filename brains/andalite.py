import pprint
from sapiens import Sapiens

class Andalite(Sapiens):
    name = 'andalite'

    def __init__(self, game, args=None):
        Sapiens.__init__(self, game, args)

    def Step(self):
        pprint.pprint(self.game.ReadBytesInRange(0xcc24, 0xcc35)) # menu data
        return Sapiens.Step(self)

    def Event(self, evt):
        Sapiens.Event(self, evt)

    def Path(self):
        return Sapiens.Path(self)

    def Victory(self):
        return Sapiens.Victory(self)

LoadedBrain = Andalite
