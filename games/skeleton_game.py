#!/usr/bin/env python2

import pygame
from pickle import dumps, loads

xmax = 320  # fallback width of the screen
ymax = 200  # fallback height of the screen


class Game:
    name = 'unnamed game'

    def __init__(self):
        pass

    # return a copy of the "screen" for visualization
    def Draw(self):
        ret = pygame.Surface((xmax, ymax))
        ret.fill((0, 123, 45))
        return ret

    # return some copy of the game's state
    def Freeze(self):
        return dumps(self.__dict__)

    # restore a saved state returned by Freeze
    def Thaw(self, state):
        self.__dict__ = loads(state)

    # set the state of the "control pad" and run a frame
    def Input(self, data):
        pass

    # must return an iterable of all possible inputs
    def ValidInputs(self):
        return [0]

    # return a dict of button mappings to input bitmasks
    def HumanInputs(self):
        return {0: 0}

    # return the screen (width, height) that should be used
    def ScreenSize(self):
        return xmax, ymax

    # return left and right channel, 16-bit sound
    def Sound(self):
        return 0, 0


LoadedGame = Game
