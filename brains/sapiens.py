#!/usr/bin/env python2

import pygame

from skeleton_solver import Brain

pygame.joystick.init()
joylist = [pygame.joystick.Joystick(i).get_name()
           for i in range(pygame.joystick.get_count())] or [-1]


class Sapiens(Brain):
    name = 'sapiens'

    def __init__(self, game, *_, joypad=joylist[0], dir_keys='wsad', btn_keys='klji1056',
                 state_path='output/{name}.state'):
        Brain.__init__(self, game)

        if type(joypad) == str:
            if joypad.isdigit():
                joypad = int(joypad)
            else:
                joypad = joylist.index(joypad)
        if joypad >= 0:
            self.joy = pygame.joystick.Joystick(joypad)
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
        for i in range(len(dir_keys)):
            s = 'hat0_{}'.format(UDLR[i])
            if s in map:
                self.key_map[ord(dir_keys[i])] = map[s]
        for i in range(len(btn_keys)):
            if i in map:
                self.key_map[ord(btn_keys[i])] = map[i]

        self.state_path = state_path.format(name=self.game.name.lower())

    def Step(self):
        self.game.Input(self.pad)
        self.input_log.append(self.pad)
        pygame.display.set_caption('{}'.format(self.game.name))
        return self.game.Draw(),

    def Event(self, evt):
        self._event_pad(evt)
        self._event_hotkeys(evt)

    def _event_pad(self, evt):
        if evt.type == pygame.JOYHATMOTION:
            hat = evt.value
            lut = self.hat_lut
            self.pad &= self.hat_reset
            for i in (0, 1):
                if hat[i] in lut[i]:
                    name = 'hat0_{}'.format(lut[i][hat[i]])
                    if name in self.input_map:
                        self.pad |= self.input_map[name]
        elif evt.type == pygame.JOYBUTTONDOWN:
            if evt.button in self.input_map:
                self.pad |= self.input_map[evt.button]
        elif evt.type == pygame.JOYBUTTONUP:
            if evt.button in self.input_map:
                self.pad &= ~self.input_map[evt.button]
        elif evt.type == pygame.KEYDOWN:
            if evt.key in self.key_map:
                self.pad |= self.key_map[evt.key]
        elif evt.type == pygame.KEYUP:
            if evt.key in self.key_map:
                self.pad &= ~self.key_map[evt.key]

    def _event_hotkeys(self, evt):
        if evt.type == pygame.KEYDOWN:
            if evt.key == pygame.K_F2:
                with open(self.state_path, 'wb') as f:
                    f.write(self.game.Freeze())
            elif evt.key == pygame.K_F4:
                with open(self.state_path, 'rb') as f:
                    self.game.Thaw(f.read())
            elif evt.key == pygame.K_SPACE:
                self.game.limit_fps = False
        elif evt.type == pygame.KEYUP:
            if evt.key == pygame.K_SPACE:
                self.game.limit_fps = True

    def Path(self):
        return self.input_log

LoadedBrain = Sapiens
