from sync.games import *

# Add games here as they are supported.
gameSyncMap = {
    'POKEMON BLUE': pkmnrb.PokemonRedBlueSync,
    'POKEMON RED': pkmnrb.PokemonRedBlueSync
}

def get_game_sync_class(gameName):
    game_sync = gameSyncMap.get(gameName)
    if game_sync == None:
        return None
    return game_sync
