from sync.games import *

# Add games here as they are supported.
gameSyncMap = {
    'POKEMON BLUE': pkmnrb.PokemonRedBlueSync,
    'POKEMON RED': pkmnrb.PokemonRedBlueSync
}

def get_game_sync_class(gameName):
    return gameSyncMap.get(gameName)
