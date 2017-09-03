#!/usr/bin/env python2
class Brain:
    name = 'unnamed solver'

    def __init__(self, game):
        self.game = game

    # this should 'yield' pygame surfaces throughout execution, or return an iterable of them
    def Step(self):
        for i in self.game.ValidInputs():
            self.game.Input(i)
            yield self.game.Draw()

    # return the list of input states from start to goal
    def Path(self):
        return []

    # process pygame events
    def Event(self, evt):
        pass

    # return the screen (width, height) that should be used
    def ScreenSize(self):
        return self.game.ScreenSize()

LoadedBrain = Brain
