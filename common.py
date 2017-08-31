#!/usr/bin/env python2

import pygame  # this level was removed from Donkey Kong for its NES release
import pickle  # a sea cucumber left in brine
import os  # generic brand cheerios
import sys  # a nickname that refers to a female sybling
import time  # an illusion

game_path = './games'
brain_path = './brains'

blacklist = ['skeleton_game', 'skeleton_solver']

sys.path.append(game_path)
sys.path.append(brain_path)
sys.path.append('./deps/python-retro')  # hack


class UtilType:
    def __init__(self):
        pass

    @staticmethod
    def ListModules(path):
        files = os.listdir(path)
        for i in files:
            if '.' in i:
                name, ext = i.rsplit('.', 1)
                if ext == 'py' and name not in blacklist:
                    yield name

    def ListGames(self):
        return self.ListModules(game_path)

    def ListBrains(self):
        return self.ListModules(brain_path)

    @staticmethod
    def GetArgs(modname):
        mod = __import__(modname)
        validators = {}
        if hasattr(mod, 'validargs'):
            validators = mod.validargs
        return mod.defaultargs.copy(), validators.copy()


util = UtilType()


class Driver:
    def __init__(self, game, brain, game_args, brain_args):
        self.game = game(**game_args)
        self.brain = brain(self.game, **brain_args)

        self.game_args = game_args
        self.brain_args = brain_args

        self.win_size = self.brain.ScreenSize()
        self.screen = pygame.display.set_mode(self.win_size)

    def Run(self):
        running = True
        print('Driver: Started at', time.asctime())
        while running:
            # let the pathfinder take a step, get screens to show throughout
            for surf in self.brain.Step():
                # process events
                for event in pygame.event.get():
                    # pass events on to the pathfinder in case it takes input etc.
                    self.brain.Event(event)
                    if event.type == pygame.QUIT:
                        running = False
                # if relevant, draw the screen
                if surf is not None:
                    self.screen.blit(surf, (0, 0))
                pygame.display.flip()
            pygame.display.flip()

        print('Driver: Finished at', time.asctime())

    def Save(self, output, screenshot=None):
        result = {
            'game': self.game.name,
            'game_args': self.game_args,
            'brain': self.brain.name,
            'brain_args': self.brain_args,
            'path': self.brain.Path(),
            'state': self.game.Freeze()
        }
        pickle.dump(result, open(output, 'wb'))

        if screenshot is not None:
            pygame.image.save(self.screen, screenshot)
