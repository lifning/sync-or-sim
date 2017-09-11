from sync.interfaces import IStrategy
from sync.strategies.simple_onchange import SimpleOnChangeStrategy
import visualization.textlog


class AsymmetricalOnChangeStrategy(SimpleOnChangeStrategy):

    # A strategy that watches emulator memory & sends it when a change is detected
    # and applies data immediately when it is received (before collecting data to send)
    def __init__(self, offset_length_pairs, write_offset, label):
        SimpleOnChangeStrategy.__init__(self, offset_length_pairs, label)
        self.write_offset = write_offset

    def write_received_data_to_memory(self, caller, received_data):
        received_something = False
        for data in received_data:
            offset = data.get('offset')
            if offset in self.interesting_offsets:
                received_something = True
                mem = data.get('data')
                bank_switch = data.get('bank_switch', 0)
                caller.write_memory(offset + self.write_offset, mem, bank_switch)

        if received_something:
            visualization.textlog.log_text(f"Received {self.label}")

