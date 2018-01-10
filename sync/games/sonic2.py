from enum import Enum
from sync.primitives import IGameSync, MirroredAddress
from sync.strategies.simple_onchange import SimpleOnChangeStrategy

ANIMATION_DYING = 0x18
RESPAWN_WAIT_TIME = 200  # wait this many frames before allowing the player to jump back in.

class LifeState(Enum):
    ALIVE = 1
    DYING = 2
    RESPAWNING = 3

class Sonic2Sync(IGameSync):
    """
    http://info.sonicretro.org/SCHG:Sonic_2/RAM_Editing
    https://github.com/sonicretro/s2disasm
    """

    def __init__(self, send_data_callback, apply_data_callback):
        IGameSync.__init__(self, send_data_callback, apply_data_callback)
        self.player_position_strategy = SimpleOnChangeStrategy([
            MirroredAddress(0x10, 0xb008, 0xb048),  # pos, vel, inertia, radius
            MirroredAddress(0x1, 0xb022, 0xb062),  # status
            MirroredAddress(0x18, 0xb028, 0xb068),  # other sonic/tails-specific object fields
            MirroredAddress(0x2, 0xf604, 0xf606),  # shadow gamepad, need ROM patched to not clobber
            MirroredAddress(0x2, 0xf602, 0xf66a),  # shadow gamepad (logical)
            MirroredAddress(0x2, 0xfe10, should_write=False),  # zone & act number
        ], "sonic -> tails")
        self.strats.append(self.player_position_strategy)
        self.life_state = LifeState.ALIVE
        self.time_in_respawning_state = 0

    def handle_respawn(self):
        # enhanced respawning which allows you to spectate the other player if you've just died
        # and jump back into the action by pressing any button on your controller

        num_lives = int.from_bytes(self.read_memory(0xfe12, 2, 0), byteorder='big', signed=False)
        animation = int.from_bytes(self.read_memory(0xb01c, 1, 0), byteorder='big', signed=False)

        if self.life_state == LifeState.RESPAWNING:
            self.time_in_respawning_state += 1

            # apply other player's position to you
            other_player_pos = (self.player_position_strategy.get_last_received_value(0xb048, 0x10))
            self.write_memory(0xb008, other_player_pos, 0)
            self.write_memory(0xb030, b'\x00\x78', 0)  # set invulnerability time

            held_keys = self.read_memory(0xf604, 1, 0)

            # If you press a button and it's been enough frames, exit respawning state.
            if held_keys != b'\x00' and self.time_in_respawning_state > RESPAWN_WAIT_TIME:
                self.time_in_respawning_state = 0
                self.life_state = LifeState.ALIVE
                self.write_memory(0xb030, b'\x00\x00', 0)  # clear invulnerability time

        if self.life_state == LifeState.ALIVE and animation == ANIMATION_DYING:
            self.life_state = LifeState.DYING

        if self.life_state == LifeState.DYING and animation != ANIMATION_DYING:
            self.life_state = LifeState.RESPAWNING

        if num_lives < 69:
            self.write_memory(0xfe12, b'\x00\x45', 0)
            self.write_memory(0xfe1c, b'\x01\x01\x01\x01', 0)  # redraw whole hud

    def on_emulator_step(self, received_data):
        # if the other player isn't in the same zone or act, change some state
        current_level = self.read_memory(0xfe10, 2, 0)
        other_player_level = self.player_position_strategy.get_last_received_value(0xfe10, 2)
        if current_level != other_player_level:
            if self.life_state == LifeState.RESPAWNING:
                self.life_state = LifeState.ALIVE
                self.write_memory(0xb030, b'\x00\x00', 0)  # clear invulnerability time

        self.write_memory(0xf702, b'\x77\x77', 0)  # force CPU tails to never take over
        self.write_memory(0xf704, b'\x00\x00', 0)  # force tails to never helicopter-respawn

        self.handle_respawn()

        return super().on_emulator_step(received_data)
