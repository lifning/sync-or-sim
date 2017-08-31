#!/usr/bin/env python2

import getopt
import sys

import common

# default game and solver to use
game_mod_name, brain_mod_name = ('superopti', 'andalite')
game_args, brain_args = ({}, {})

replay_output = 'output/last_run.pickle'  # default value for the output pickle

all_games = list(common.util.ListGames())
all_brains = list(common.util.ListBrains())


if __name__ == "__main__":
    # parse command line arguments
    opts, args = getopt.getopt(sys.argv[1:], "g:b:", ["game=", "brain="])

    for o, a in opts:
        if o in ('-g', '--game'):
            subargs = a.split('@')
            game_mod_name = subargs[0]
            for i in subargs[1:]:
                key, val = i.split(':')
                game_args[key] = val
        elif o in ('-b', '--brain'):
            subargs = a.split('@')
            brain_mod_name = subargs[0]
            for i in subargs[1:]:
                key, val = i.split(':')
                brain_args[key] = val

    # run optiness with parsed arguments
    driver = common.Driver(game_mod_name, brain_mod_name, game_args, brain_args)
    driver.Run()
    driver.Save(replay_output)
