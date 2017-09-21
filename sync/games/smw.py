from sync.primitives import IGameSync
from sync.strategies.simple_onchange import SimpleOnChangeStrategy


class SuperMarioWorldSync(IGameSync):
    def __init__(self, send_data_callback, apply_data_callback):
        IGameSync.__init__(self, send_data_callback, apply_data_callback)
        self.strats.append(SimpleOnChangeStrategy([(0x7a, 4)], "velocity"))
