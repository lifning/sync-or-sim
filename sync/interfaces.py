class IGameSync:
    def __init__(self, read_memory_callback, write_memory_callback):
        self.read_memory = read_memory_callback
        self.write_memory = write_memory_callback

    # return any data that should be sent from this step
    def on_emulator_step(self, received_data):
        raise NotImplementedError

class IStrategy:
    def on_emulator_step(self, caller, received_data):
        raise NotImplementedError

