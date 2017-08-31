#!/usr/bin/env python2

import pygame

from skeleton_solver import Brain

pygame.joystick.init()  # hack to allow argument validation
joylist = [pygame.joystick.Joystick(i).get_name() for i in range(pygame.joystick.get_count())]

def get_default_joystick():
    if joylist:
        return joylist[0]
    return None

defaultargs = {'joynum': get_default_joystick(),
               'keyhat': 'wsad',
               'keybuttons': 'klji1056'}

# lambda x: x == 0 or (x > 0 and x < pygame.joystick.get_count()) }

class Sapiens(Brain):
    name = 'sapiens'

    def __init__(self, game, **kwargs):
        Brain.__init__(self, game, defaultargs, **kwargs)

        joynum = self.args['joynum']
        if type(joynum) == str:
            joynum = joylist.index(joynum)
        if joynum and joynum >= 0:
            self.joy = pygame.joystick.Joystick(joynum)
            self.joy.init()
            print('Sapiens:', self.joy.get_name())

        self.input_log = []
        self.input_map = game.HumanInputs()
        self.pad = 0

        UDLR = ('up', 'down', 'left', 'right')

        map = self.input_map
        self.hat_reset = 0
        for i in UDLR:
            s = 'hat0_{}'.format(i)
            if s in map:
                self.hat_reset |= map[s]
        self.hat_reset = ~self.hat_reset
        self.hat_lut = [{-1: 'left', 1: 'right'},
                        {1: 'up', -1: 'down'}]

        self.key_map = {}
        keyhat = self.args['keyhat']
        for i in range(len(keyhat)):
            s = 'hat0_{}'.format(UDLR[i])
            if s in map:
                self.key_map[ord(keyhat[i])] = map[s]
        keybuttons = self.args['keybuttons']
        for i in range(len(keybuttons)):
            if i in map:
                self.key_map[ord(keybuttons[i])] = map[i]

    def Step(self):
        self.game.Input(self.pad)
        self.input_log.append(self.pad)
        pygame.display.set_caption('{}'.format(self.game.name))
        return self.game.Draw(),

    def Event(self, evt):
        imap = self.input_map
        kmap = self.key_map
        if evt.type == pygame.JOYHATMOTION:
            hat = evt.value
            lut = self.hat_lut
            self.pad &= self.hat_reset
            for i in (0, 1):
                if hat[i] in lut[i]:
                    name = 'hat0_{}'.format(lut[i][hat[i]])
                    if name in imap:
                        self.pad |= imap[name]
        elif evt.type == pygame.JOYBUTTONDOWN:
            if evt.button in imap:
                self.pad |= imap[evt.button]
        elif evt.type == pygame.JOYBUTTONUP:
            if evt.button in imap:
                self.pad &= ~imap[evt.button]
        elif evt.type == pygame.KEYDOWN:
            if evt.key in kmap:
                self.pad |= kmap[evt.key]
        elif evt.type == pygame.KEYUP:
            if evt.key in kmap:
                self.pad &= ~kmap[evt.key]

    def Path(self):
        return self.input_log

    def Victory(self):
        return False


LoadedBrain = Sapiens
