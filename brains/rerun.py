#!/usr/bin/env python2

import wave
from array import array

import pickle
import pygame

from skeleton_solver import Brain

default_args = {'file': 'output/last_run.pickle',
                'force': False,
                'recordvideo': False,
                'recordaudio': False}


class Rerun(Brain):
    name = 'rerun'

    def __init__(self, game, **kwargs):
        Brain.__init__(self, game, default_args, **kwargs)

        self.force = self.args['force']
        self.recordvideo = self.args['recordvideo']
        self.recordaudio = self.args['recordaudio']

        loadedfile = pickle.load(open(self.args['file'], 'rb'))

        if self.recordaudio:
            self.wav = wave.open('output/{}_{}.wav'.format(self.__class__.name, self.game.__class__.name), 'wb')
            self.wav.setnchannels(2)
            self.wav.setsampwidth(2)
            # HACK: specific to superopti
            self.wav.setframerate(int(self.game.emu.get_av_info()['sample_rate']) or 32040)

        # describe the run
        print('replaying a run of:\t', loadedfile['game'], '\t', loadedfile['game_args'])
        print('that was produced by:\t', loadedfile['brain'], '\t', loadedfile['brain_args'])
        if not self.force:
            if loadedfile['game'] != game.__class__.name:
                raise Exception('loaded input string is for "%s"' % (loadedfile['game']))

            mismatches = []
            for key in game.args:
                if key == 'audio':
                    print('rerun: be sure to use "array" for the game audio if you want to use rerun\'s sound recording.')
                else:
                    # note: old args being dropped are implicitly ignored by this loop.
                    # explicitly ignore new features with this conditional.
                    if key in loadedfile['game_args'] and loadedfile['game_args'][key] != game.args[key]:
                        mismatches.append(key)
            if len(mismatches) > 0:
                for key in mismatches:
                    print(key, '\n\tgame:', game.args[key], end=' ')
                    print('\n\tfile:', loadedfile['game_args'][key])
                raise Exception('game_args mismatch')

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
                pygame.image.save(surf,
                                  'output/%s_%s_%04d.png' % (self.__class__.name,
                                                             self.game.__class__.name,
                                                             len(self.outputstring)))
            if self.recordaudio:
                self.wav.writeframesraw(array('H', self.game.Sound()).tostring())

        else:
            surf = self.game.Draw()
            self.wav.close()

        yield surf

    def Path(self):
        return self.outputstring + self.inputstring

    def Victory(self):
        return not self.inputstring


LoadedBrain = Rerun
