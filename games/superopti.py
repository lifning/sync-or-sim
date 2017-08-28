#!/usr/bin/env python2

import os
import pygame

from skeleton_game import Game

import py_retro as retro

defaultargs = {'libretro': 'data/gambatte_libretro.dll',
               'rom': 'data/pokeblue.gb',
               'padoverlay': True}

validargs = {'libretro': os.path.isfile, 'rom': os.path.isfile, }


class SnesPadDrawing:
    def __init__(self, alpha=255, name='SUPER NES'):
        bg = (200, 200, 200)
        fg = (150, 150, 150)
        black = (50, 50, 50)

        ctrlr = pygame.Surface((250, 110))
        ctrlr.fill((0, 0, 0))
        ctrlr.set_colorkey((0, 0, 0))
        ctrlr.set_alpha(alpha)

        pygame.font.init()
        bold = pygame.font.Font(None, 12)
        bold.set_bold(True)
        italic = pygame.font.Font(None, 8)
        italic.set_italic(True)
        logo = pygame.font.Font(None, 16)
        logo.set_italic(True)
        logo.set_underline(True)

        # frame
        pygame.draw.circle(ctrlr, bg, (55, 55), 50)
        pygame.draw.rect(ctrlr, bg, (55, 5, 140, 90))
        pygame.draw.circle(ctrlr, bg, (195, 55), 50)
        pygame.draw.circle(ctrlr, fg, (55, 55), 25, 1)
        pygame.draw.circle(ctrlr, fg, (195, 55), 45)

        # dpad center
        pygame.draw.circle(ctrlr, black, (55, 55), 7)

        # bayx outlines
        pygame.draw.line(ctrlr, bg, (195, 74), (220, 54), 21)
        pygame.draw.circle(ctrlr, bg, (195, 75), 10)
        pygame.draw.circle(ctrlr, bg, (220, 55), 10)
        pygame.draw.line(ctrlr, bg, (172, 54), (195, 36), 21)
        pygame.draw.circle(ctrlr, bg, (172, 55), 10)
        pygame.draw.circle(ctrlr, bg, (195, 35), 10)

        # text
        ctrlr.blit(logo.render(name, True, black), (85, 10))
        ctrlr.blit(italic.render('SELECT', True, black), (94, 75))
        ctrlr.blit(italic.render('START', True, black), (122, 75))
        ctrlr.blit(bold.render('Y', True, bg), (155, 65))
        ctrlr.blit(bold.render('B', True, bg), (176, 84))
        ctrlr.blit(bold.render('X', True, bg), (209, 21))
        ctrlr.blit(bold.render('A', True, bg), (230, 40))

        self.frame = ctrlr

    def Draw(self, pad):
        B, Y, Se, St, Up, Down, Left, Right, A, X, L, R = [pad & (1 << i) for i in range(12)]

        bg = (200, 200, 200)
        fg = (150, 150, 150)
        black = (50, 50, 50)

        red = (100, 0, 150)
        yellow = red
        blue = (150, 50, 200)
        green = blue
        # red = (200,50,0)
        # yellow = (250,200,0)
        # blue = (0,0,200)
        # green = (50,200,0)

        ctrlr = self.frame.copy()

        # dpad
        if Up:    pygame.draw.rect(ctrlr, black, (47, 35, 15, 20))
        if Down:  pygame.draw.rect(ctrlr, black, (47, 55, 15, 20))
        if Left:  pygame.draw.rect(ctrlr, black, (35, 47, 20, 15))
        if Right: pygame.draw.rect(ctrlr, black, (55, 47, 20, 15))

        # select/start
        if Se: pygame.draw.line(ctrlr, black, (100, 67), (110, 60), 10)
        if St: pygame.draw.line(ctrlr, black, (125, 67), (135, 60), 10)

        # ba
        if B: pygame.draw.circle(ctrlr, yellow, (195, 75), 8)
        if A: pygame.draw.circle(ctrlr, red, (220, 55), 8)

        # yx
        if Y: pygame.draw.circle(ctrlr, green, (172, 55), 8)
        if X: pygame.draw.circle(ctrlr, blue, (195, 35), 8)

        # lr
        if L:
            pygame.draw.lines(ctrlr, bg, True, ((30, 9), (48, 3), (80, 3)), 2)
            pygame.draw.lines(ctrlr, fg, False, ((30, 11), (48, 5), (80, 5)), 1)
        if R:
            pygame.draw.lines(ctrlr, bg, True, ((168, 3), (200, 3), (220, 9)), 2)
            pygame.draw.lines(ctrlr, fg, False, ((168, 5), (200, 5), (220, 11)), 1)

        return ctrlr


class SuperOpti(Game):
    name = 'superopti'

    def __init__(self, args=None):
        if args is None:
            args = {}

        Game.__init__(self, args, defaultargs, validargs)

        # load the libretro core and feed the emulator a ROM
        self.emu = retro.core.EmulatedSNES(args['libretro'])
        self.emu.load_cartridge_normal(open(args['rom'], 'rb').read())

        # register rendering and input-reading callbacks
        self.snesfb = pygame.Surface(self.emu.get_av_info()['base_size'])
        retro.pygame_video.set_video_refresh_surface(self.emu, self.snesfb)
        retro.portaudio_audio.set_audio_sample_internal(self.emu)
        retro.simple_input.set_input_internal(self.emu)

        # unplug player 2 controller so we don't get twice as many input state callbacks
        self.emu.set_controller_port_device(1, retro.DEVICE_NONE)

        # don't put anything in the work ram until the emulator can
        self.wram = None
        self.pad = 0

        # showing what buttons are active
        self.padoverlay = None
        if self.args['padoverlay']:
            self.padoverlay = SnesPadDrawing(name='SUPER SYNC')

    def HumanInputs(self):
        return {'hat0_up': 0b000000010000,
                'hat0_down': 0b000000100000,
                'hat0_left': 0b000001000000,
                'hat0_right': 0b000010000000,
                0: 0b000000000001,
                1: 0b000100000000,
                2: 0b000000000010,
                3: 0b001000000000,
                4: 0b010000000000,
                5: 0b100000000000,
                6: 0b000000000100,
                7: 0b000000001000}

    def Freeze(self):
        return self.emu.serialize()

    def Thaw(self, state):
        self.emu.unserialize(state)
        self.wram = self.emu.memory_to_string(retro.core.MEMORY_WRAM)

    # only convert the screen from 16-bit format to RGB888 when we need it
    def Draw(self):
        # if we don't have something to draw, or if there's no point in drawing it
        if self.snesfb is None or not pygame.display.get_active():
            return None

        game_img = self.snesfb

        # draw the gamepad underneath if enabled
        if self.padoverlay is not None:
            pad_img = self.padoverlay.Draw(self.pad)
            joined = pygame.Surface(self.ScreenSize())
            joined.blit(game_img, (0, 0))
            joined.blit(pad_img, (3, game_img.get_height()))
            return joined


        return game_img

    def Input(self, pad):
        # update the internal pad state that will be checked with libretro' callbacks
        self.pad = pad
        retro.simple_input.set_state_digital(0, pad)

        # run for the specified number of frames on that pad state
        self.emu.run(1)

        # fetch the work RAM
        self.wram = self.emu.memory_to_string(retro.MEMORY_WRAM)
        if self.wram is None:
            print('SuperOpti: error retrieving RAM')

    def _Byte(self, ofs):
        if self.wram is None:
            return 0
        return ord(self.wram[ofs])

    def _Word(self, ofshi, ofslo):
        return (self._Byte(ofshi) << 8) | self._Byte(ofslo)

    def ScreenSize(self):
        # w,h = self.args['screen']
        w, h = self.snesfb.get_size()
        if self.padoverlay is not None:
            w = max(256, w)
            h += self.padoverlay.frame.get_height()
        return w, h


LoadedGame = SuperOpti
