from sync.interfaces import IGameSync
from sync.strategies.asymmetrical_onchange import AsymmetricalOnChangeStrategy


class Sonic2Sync(IGameSync):
    def __init__(self, send_data_callback, apply_data_callback):
        IGameSync.__init__(self, send_data_callback, apply_data_callback)

        # sync items separately since they're less sensitive.
        self.physics = AsymmetricalOnChangeStrategy([(0xb008, 0x16)], 0x40, "sonic -> tails")
        self.skip_frame = False

    def on_emulator_step(self, received_data):
        self.skip_frame = not self.skip_frame
        if self.skip_frame: return
        updates = self.physics.on_emulator_step(self, received_data)

        return updates
