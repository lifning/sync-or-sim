from sync.interfaces import IStrategy
import visualization.textlog


class SimpleOnChangeStrategy(IStrategy):
    last_seen = {}

    # A strategy that watches emulator memory & sends it when a change is detected
    # and applies data immediately when it is received (before collecting data to send)
    def __init__(self, offset_length_pairs, label):
        self.offset_length_pairs = offset_length_pairs
        self.interesting_offsets = [tup[0] for tup in offset_length_pairs]
        self.label = label

    def on_emulator_step(self, caller, received_data):
        self.write_received_data_to_memory(caller, received_data)
        data_to_send = self.read_memory_for_changes(caller)
        return data_to_send

    def read_memory_for_changes(self, caller):
        # this sends all the interesting offsets' data, or none, never a partial subset.
        change_seen = False
        data_to_send = []
        for tup in self.offset_length_pairs:
            offset, length = tup[0:2]
            bank_switch = tup[2] if len(tup) == 3 else 0
            d = {'offset': offset,
                 'data': caller.read_memory(offset, length, bank_switch),
                 'bank_switch': bank_switch,
                 }
            data_to_send.append(d)

            # compare this with the last seen version
            key = (offset, bank_switch)
            last_seen_data = self.last_seen.get(key)
            if last_seen_data != d:
                change_seen = True
                self.last_seen[key] = d  # write it back

        if change_seen:
            visualization.textlog.log_text(f"Sending {self.label}")
            return data_to_send
        return []  # no change? send nothing.

    def write_received_data_to_memory(self, caller, received_data):
        received_something = False
        for data in received_data:
            offset = data.get('offset')
            if offset in self.interesting_offsets:
                received_something = True
                mem = data.get('data')
                bank_switch = data.get('bank_switch', 0)
                caller.write_memory(offset, mem, bank_switch)
                # also update last_seen so we don't send back something that we just wrote.
                key = (offset, bank_switch)
                self.last_seen[key] = data

        if received_something:
            visualization.textlog.log_text(f"Received {self.label}")

