import pprint
from sapiens import Sapiens

def ReadBytesInRange(game, startOffset, endOffset):
    if endOffset - startOffset <= 0:
        return None

    b = {}

    for offset in range(startOffset, endOffset + 1):
        b[offset] = game._Byte(offset)

    return b

class Andalite(Sapiens):
    name = 'andalite'

    def __init__(self, game, args=None):
        Sapiens.__init__(self, game, args)

    def Step(self):
        pprint.pprint(ReadBytesInRange(self.game, 0xa598, 0xa5a2))
        return Sapiens.Step(self)

    def Event(self, evt):
        Sapiens.Event(self, evt)

    def Path(self):
        return Sapiens.Path(self)

    def Victory(self):
        return Sapiens.Victory(self)

LoadedBrain = Andalite
