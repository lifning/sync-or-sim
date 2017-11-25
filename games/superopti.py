#!/usr/bin/env python2

import pygame

import py_retro as retro
from skeleton_game import Game
from visualization.snespad import SnesPadDrawing
import visualization.textlog


class SuperOpti(Game):
    name = 'superopti'

    def __init__(self, *_, libretro='data/gambatte_libretro.dll', rom='data/pokeblue.gb',
                 state='data/pokeblue.state', draw_pad=False, scale_factor=1):
        Game.__init__(self)

        self.screen_size = (1, 1)
        self.framebuffer = None

        # load the libretro core and feed the emulator a ROM
        self.emu = retro.core.EmulatedSystem(libretro)
        self.emu.load_game_normal(open(rom, 'rb').read(), path=rom)
        self.name = self.emu.name

        # load a starting state if one was provided
        try:
            with open(state or '', 'rb') as f:
                self.Thaw(f.read())
        except IOError:
            pass

        # showing what buttons are active
        self.pad = 0
        self.pad_overlay = SnesPadDrawing(name='SUPER SYNC') if draw_pad else None

        # register rendering and input-reading callbacks
        self._register_video_refresh()
        # disabled until there's a decent audio implementation
        # retro.portaudio_audio.set_audio_sample_internal(self.emu)
        retro.simple_input.set_input_internal(self.emu)

        # unplug player 2 controller so we don't get twice as many input state callbacks
        self.emu.set_controller_port_device(1, retro.DEVICE_NONE)

        # limit FPS
        self.clock = pygame.time.Clock()
        self.limit_fps = True

    def _register_video_refresh(self):
        if self.emu.av_info_changed:
            av_info = self.emu.get_av_info()
            print(av_info)
            self.fps = av_info['fps']
            self.screen_size = av_info['base_size']
            self.framebuffer = None
        screen = pygame.display.get_surface()
        if self.framebuffer is None and screen is not None:
            self.framebuffer = screen.subsurface(pygame.Rect((0, 0), self.screen_size))
            retro.pygame_video.set_video_refresh_surface(self.emu, self.framebuffer)

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
        if not pygame.display.get_active():
            return

        # check for runtime mode-setting
        self._register_video_refresh()
        game_img = self.framebuffer

        # draw the gamepad underneath if enabled
        # FIXME: this is super inefficient
        # - needs to not redraw if no pad state change
        # - needs to not allocate a new screen-sized Surface every frame
        if game_img is not None and self.pad_overlay is not None:
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
        if self.limit_fps:
            self.clock.tick(self.fps)

    def ScreenSize(self):
        w, h = self.screen_size
        if self.pad_overlay is not None:
            w = max(256, w)
            h += self.pad_overlay.frame.get_height()

        return w, h

    def PeekMemoryRegion(self, offset, length, bank_switch):
        return self.emu.peek_memory_region(offset, length, bank_switch)

    def PokeMemoryRegion(self, offset, data, bank_switch):
        self.emu.poke_memory_region(offset, data, bank_switch)

LoadedGame = SuperOpti
