from sync.primitives import IGameSync, MirroredAddress
from sync.strategies.simple_onchange import SimpleOnChangeStrategy


class Sonic2Sync(IGameSync):
    """
    http://info.sonicretro.org/SCHG:Sonic_2/RAM_Editing
    https://github.com/sonicretro/s2disasm
    """
    def __init__(self, send_data_callback, apply_data_callback):
        IGameSync.__init__(self, send_data_callback, apply_data_callback)
        self.strats.append(SimpleOnChangeStrategy([
            MirroredAddress(0x10, 0xb008, 0xb048),  # pos, vel, inertia, radius
            MirroredAddress(0x1, 0xb022, 0xb062),  # status
            MirroredAddress(0x18, 0xb028, 0xb068),  # other sonic/tails-specific object fields
            MirroredAddress(0x2, 0xf604, 0xf606),  # shadow gamepad, need ROM patched to not clobber
            MirroredAddress(0x2, 0xf602, 0xf66a),  # shadow gamepad (logical)
        ], "sonic -> tails"))

    def on_emulator_step(self, received_data):
        self.write_memory(0xf702, b'\x77\x77', 0)  # force CPU tails to never take over
        self.write_memory(0xf704, b'\x00\x00', 0)  # force tails to never helicopter-respawn

        return super().on_emulator_step(received_data)
