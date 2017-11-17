#!/usr/bin/env python2

import wave
from array import array

import pickle
import pygame_sdl2 as pygame

from skeleton_solver import Brain


class Rerun(Brain):
    name = 'rerun'

    def __init__(self, game, *_,
                 replay_input='output/last_run.pickle', write_png=False, write_wav=False,
                 skip_valid_check=False):
        Brain.__init__(self, game)

        self.recordvideo = write_png
        self.recordaudio = write_wav

        loadedfile = pickle.load(open(replay_input, 'rb'))

        if self.recordaudio:
            self.wav = wave.open('output/{}_{}.wav'.format(self.name, self.game.name), 'wb')
            self.wav.setnchannels(2)
            self.wav.setsampwidth(2)
            # HACK: specific to superopti
            self.wav.setframerate(int(self.game.emu.get_av_info()['sample_rate']) or 32040)

        # describe the run
        print('replaying a run of:\t', loadedfile['game'], '\t', loadedfile['game_args'])
        print('that was produced by:\t', loadedfile['brain'], '\t', loadedfile['brain_args'])
        if not skip_valid_check:
            if loadedfile['game'] != game.name:
                raise Exception('loaded input string is for "%s"' % (loadedfile['game']))

        self.inputstring = loadedfile['path']
        self.outputstring = []
        print('with', len(self.inputstring), 'frames of input')

    def Step(self):
        if self.inputstring:
            frameinput = self.inputstring.pop(0)
            self.outputstring.append(frameinput)

            self.game.Input(frameinput)
            surf = self.game.Draw()

            if self.recordvideo:
                pygame.image.save(surf, 'output/%s_%s_%04d.png' % (self.name, self.game.name,
                                                                   len(self.outputstring)))
            if self.recordaudio:
                self.wav.writeframesraw(array('H', self.game.Sound()).tostring())
        else:
            self.game.Input(0)
            surf = self.game.Draw()
            if self.recordaudio:
                self.wav.close()
                self.recordaudio = False

        yield surf

    def Path(self):
        return self.outputstring + self.inputstring

LoadedBrain = Rerun
