#!/usr/bin/env python2

import argparse
import inspect

import itertools

import common


# adds any arguments appearing after *_ in a class' constructor as an argument group.
def add_constructor_params(parser, cls):
    group = parser.add_argument_group(cls.name)
    for param in inspect.signature(cls.__init__).parameters.values():
        assert isinstance(param, inspect.Parameter)
        if param.kind == param.KEYWORD_ONLY:
            flag = '--{}'.format(param.name.replace('_', '-'))
            kw = {'dest': param.name}
            if param.default != param.empty:
                if type(param.default) == bool:
                    if param.default:
                        flag = '--no-{}'.format(param.name.replace('_', '-'))
                        kw['action'] = 'store_false'
                    else:
                        kw['action'] = 'store_true'
                else:
                    kw.update(default=param.default, type=type(param.default),
                              help='({})'.format(repr(param.default)))
            group.add_argument(flag, **kw)


def filter_args(args, cls):
    value = dict((k, v) for k, v in args.items() if k in inspect.signature(cls.__init__).parameters)
    for base in cls.__bases__:
        if base is not object:
            value.update(filter_args(args, base))
    return value


def main():
    all_games = dict((mod, __import__(mod).LoadedGame) for mod in common.util.ListGames())
    all_brains = dict((mod, __import__(mod).LoadedBrain) for mod in common.util.ListBrains())

    # defaults
    game_mod_name = 'superopti'
    brain_mod_name = 'andalite'
    replay_output = 'output/last_run.pickle'

    parser = argparse.ArgumentParser()
    parser.add_argument('--game', choices=all_games.keys(), default=game_mod_name)
    parser.add_argument('--brain', choices=all_brains.keys(), default=brain_mod_name)
    parser.add_argument('--replay-output', type=str, default=replay_output,
                        help='where to save the input log (usable by "rerun")')
    for game, cls in itertools.chain(all_games.items(), all_brains.items()):
        add_constructor_params(parser, cls)
    args = vars(parser.parse_args())

    game_mod_name = args['game']
    brain_mod_name = args['brain']
    replay_output = args['replay_output']

    game = all_games[game_mod_name]
    brain = all_brains[brain_mod_name]
    game_args = filter_args(args, game)
    brain_args = filter_args(args, brain)
    del brain_args['game']
    all_games.clear()
    all_brains.clear()

    driver = common.Driver(game, brain, game_args, brain_args)
    driver.Run()
    driver.Save(replay_output)


if __name__ == "__main__":
    main()
