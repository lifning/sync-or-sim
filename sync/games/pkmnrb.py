from sync.primitives import IGameSync
from sync.strategies.simple_onchange import SimpleOnChangeStrategy


class PokemonRedBlueSync(IGameSync):
    def __init__(self, send_data_callback, apply_data_callback):
        IGameSync.__init__(self, send_data_callback, apply_data_callback)

        self.strats.append(SimpleOnChangeStrategy([
            (0xd009, 0x27),  # active pokemon in battle
            (0xd158, 0x19e),  # player & party
            (0xcc2f, 1),  # index of pokemon currently sent out
        ], "party"))

        # sync items separately since they're less sensitive.
        self.strats.append(SimpleOnChangeStrategy([(0xd31d, 0x2c)], "items & money"))

        box_size = 0x462
        self.strats.append(SimpleOnChangeStrategy([
            (0xa84c, 1, 1),  # selected box index - FIXME: not sufficient! there's a WRAM shadow too
            (0xb0c0, box_size, 1),  # current box contents
            (0xda80, box_size),  # work RAM copy of current box contents
        ] + [
            # all 12 boxes in their canonical, inactive locations
            (0xa000 + (box_size * box), box_size, bank)
            for box in range(6)
            for bank in (2, 3)
        ], "boxes"))

    def fix_checksums(self):
        """Fix checksums *locally* (don't send to remote users for whom it might not be valid)"""
        # Alg: https://bulbapedia.bulbagarden.net/wiki/Save_data_structure_in_Generation_I#Checksum
        ck = 0
        for byte in self.read_memory(0xa598, 0xf8b, bank_switch=1):
            ck += byte
        ck = ~ck & 0xff
        old_ck = self.read_memory(0xb523, 1, bank_switch=1)[0]
        if ck != old_ck:
            print(f'Corrected checksum in SRAM bank 1: was {hex(old_ck)}, now {hex(ck)}')
        self.write_memory(0xb523, bytes([ck]), bank_switch=1)
        # TODO: the checksums in banks 2 and 3, if necessary? are they the same alg?

    def on_emulator_step(self, received_data):
        updates = super().on_emulator_step(received_data)
        if received_data:
            self.fix_checksums()
        return updates
