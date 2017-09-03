#!/usr/bin/env python2

import pygame

import py_retro as retro
from skeleton_game import Game
from visualization.snespad import SnesPadDrawing
import visualization.textlog


class SuperOpti(Game):
    name = 'superopti'

    def __init__(self, *_, libretro='data/gambatte_libretro.dll', rom='data/pokeblue.gb',
                 state='data/pokeblue.state', draw_pad=True, scalefactor=1):
        Game.__init__(self)

        # load the libretro core and feed the emulator a ROM
        self.emu = retro.core.EmulatedSystem(libretro)
        self.emu.load_game_normal(open(rom, 'rb').read())
        self.name = self.emu.name

        # load a starting state if one was provided
        try:
            with open(state or '', 'rb') as f:
                self.Thaw(f.read())
        except IOError:
            pass

        # register rendering and input-reading callbacks
        self.framebuffer = pygame.Surface(self.emu.get_av_info()['base_size'])
        retro.pygame_video.set_video_refresh_surface(self.emu, self.framebuffer)
        # disabled until there's a decent audio implementation
        # retro.portaudio_audio.set_audio_sample_internal(self.emu)
        retro.simple_input.set_input_internal(self.emu)

        # unplug player 2 controller so we don't get twice as many input state callbacks
        self.emu.set_controller_port_device(1, retro.DEVICE_NONE)

        # showing what buttons are active
        self.pad = 0
        self.pad_overlay = SnesPadDrawing(name='SUPER SYNC') if draw_pad else None

        # limit FPS
        self.fps = self.emu.get_av_info()['fps']
        self.clock = pygame.time.Clock()

        #scaling
        self.scalefactor = scalefactor

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

    # only convert the screen from 16-bit format to RGB888 when we need it
    def Draw(self):
        # if we don't have something to draw, or if there's no point in drawing it
        if self.framebuffer is None or not pygame.display.get_active():
            return None

        game_img = self.framebuffer
        if self.scalefactor != 1:
            new_size = tuple([size * self.scalefactor for size in self.framebuffer.get_size()])
            game_img = pygame.transform.scale(game_img, new_size)

        # draw the gamepad underneath if enabled
        if self.pad_overlay is not None:
            pad_img = self.pad_overlay.Draw(self.pad)
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
        self.clock.tick(self.fps)

    def ScreenSize(self):
        w, h = self.framebuffer.get_size()
        w *= self.scalefactor
        h *= self.scalefactor

        if self.pad_overlay is not None:
            w = max(256, w)
            h += self.pad_overlay.frame.get_height()
        return w, h

    def PeekMemoryRegion(self, offset, length):
        return self.emu.peek_memory_region(offset, length)

    def PokeMemoryRegion(self, offset, data):
        self.emu.poke_memory_region(offset, data)

LoadedGame = SuperOpti
