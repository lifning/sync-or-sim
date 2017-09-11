from sync.games import *

# Add games here as they are supported.
gameSyncMap = {
    'POKEMON BLUE': pkmnrb.PokemonRedBlueSync,
    'POKEMON RED': pkmnrb.PokemonRedBlueSync,
    'SUPER MARIOWORLD': smw.SuperMarioWorldSync,
    'SONIC THE HEDGEHOG 2': sonic2.Sonic2Sync,
}


def get_game_sync_class(gameName):
    return gameSyncMap.get(gameName)
