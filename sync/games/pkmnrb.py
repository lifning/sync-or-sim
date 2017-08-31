from sync.interfaces import IGameSync
from sync.strategies.simple_onchange import SimpleOnChangeStrategy

class PokemonRedBlueSync(IGameSync):
    def __init__(self, send_data_callback, apply_data_callback):
        IGameSync.__init__(self, send_data_callback, apply_data_callback)

        self.party = SimpleOnChangeStrategy([
            (0xd009, 0x27), # active pokemon in battle
            (0xd158, 0x19e), # player & party
            (0xcc2f, 1) # index of pokemon currently sent out
        ])

        # sync items separately since they're less sensitive.
        self.items = SimpleOnChangeStrategy([(0xd31d, 0x2c)])

    def on_emulator_step(self, received_data):
        return self.party.on_emulator_step(self, received_data) + self.items.on_emulator_step(self, received_data)
