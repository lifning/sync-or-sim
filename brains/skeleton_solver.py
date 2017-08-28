#!/usr/bin/env python2

import pygame


class Brain:
    name = 'unnamed solver'

    def __init__(self, game, args=None, defaultargs=None):
        if defaultargs is None:
            defaultargs = {}
        if args is None:
            args = {}
        self.game = game
        # try to convert args to appropriate types (from str)
        for i in args:
            try:
                args[i] = eval(args[i], {"__builtins__": None}, {})
            except:
                pass
        # load default values for any keys not given
        for i in defaultargs:
            if i not in args:
                args[i] = defaultargs[i]
        self.args = args
        self.terminated = False

    # Note: this should 'yield' pygame surfaces throughout execution,
    #       but it's acceptable to just 'return' a 1-tuple when finished.
    #       if no screen change was made, return None to skip updating the display
    def Step(self):
        for i in self.game.ValidInputs():
            self.game.Input(i)
        return self.game.Draw(),

    # return the list of input states from start to goal
    def Path(self):
        return []

    # handle events from pygame, if relevant
    def Event(self, evt):
        if evt.type == pygame.QUIT:
            self.terminated = True

    # return the screen (width, height) that should be used
    def ScreenSize(self):
        return self.game.ScreenSize()


LoadedBrain = Brain
