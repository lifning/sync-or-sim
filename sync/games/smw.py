from sync.interfaces import IGameSync
from sync.strategies.simple_onchange import SimpleOnChangeStrategy


class SuperMarioWorldSync(IGameSync):
    def __init__(self, send_data_callback, apply_data_callback):
        IGameSync.__init__(self, send_data_callback, apply_data_callback)

        # sync items separately since they're less sensitive.
        self.physics = SimpleOnChangeStrategy([(0x7a, 4)], "velocity")

    def fix_checksums(self):
        """Fix checksums *locally* (don't send to remote users for whom it might not be valid)"""
        pass

    def on_emulator_step(self, received_data):
        updates = self.physics.on_emulator_step(self, received_data)
        if received_data:
            self.fix_checksums()
        return updates
