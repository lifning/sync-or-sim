from sync.interfaces import IStrategy
class SimpleOnChangeStrategy(IStrategy):
    last_seen = {}

    # A strategy that watches emulator memory & sends it when a change is detected
    # and applies data immediately when it is received (before collecting data to send)
    def __init__(self, offset_length_pairs):
        self.offset_length_pairs = offset_length_pairs
        self.interesting_offsets = list(list(zip(*offset_length_pairs))[0]) # just a list of all the offsets

    def on_emulator_step(self, caller, received_data):
        self.write_received_data_to_memory(caller, received_data)
        data_to_send = self.read_memory_for_changes(caller)
        return data_to_send

    def read_memory_for_changes(self, caller):
        change_seen = False
        data_to_send = []
        for offset, length in self.offset_length_pairs:
            d = {'offset': offset, 'data': caller.read_memory(offset, length)}
            data_to_send.append(d)

            # compare this with the last seen version
            last_seen_data = self.last_seen.get(offset)
            if last_seen_data != d:
                change_seen = True
                self.last_seen[offset] = d # write it back

        if change_seen:
            return data_to_send
        return [] # no change? send nothing.

    def write_received_data_to_memory(self, caller, received_data):
        for data in received_data:
            offset = data.get('offset')
            if not offset in self.interesting_offsets:
                continue # this offset was boring, but who's to say the next isn't

            mem = data.get('data')
            caller.write_memory(offset, mem)
            self.last_seen[offset] = data # also update last_seen so we don't send back something that we just wrote.

