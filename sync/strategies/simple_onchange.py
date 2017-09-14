from sync.primitives import IStrategy, MirroredAddress
import visualization.textlog


class SimpleOnChangeStrategy(IStrategy):
    last_seen = {}

    # A strategy that watches emulator memory & sends it when a change is detected
    # and applies data immediately when it is received (before collecting data to send)
    def __init__(self, offset_length_pairs, label):
        super().__init__()
        self.addresses = [MirroredAddress(x[1], x[0], source_bank=(x[2] if len(x) > 2 else 0))
                          if isinstance(x, tuple) else x
                          for x in offset_length_pairs]
        self.buffer_size = sum(x.serializer.size for x in self.addresses)
        self.buffer = bytearray(self.buffer_size)
        self.label = label

    def on_emulator_step(self, caller, received_data):
        self.write_received_data_to_memory(caller, received_data)
        return self.read_memory_for_changes(caller)

    def read_memory_for_changes(self, caller):
        # this sends all the interesting offsets' data, or none, never a partial subset.
        change_seen = False
        produced = 0
        for addr in self.addresses:
            block = caller.read_memory(addr.source_offset, addr.size, addr.source_bank)
            addr.serializer.pack_into(self.buffer, produced,
                                      addr.target_offset, addr.target_bank, block)
            produced += addr.serializer.size

            # compare this with the last seen version
            key = (addr.source_offset, addr.source_bank)
            last_seen_data = self.last_seen.get(key)
            if last_seen_data != block:
                change_seen = True
                self.last_seen[key] = block  # write it back

        if change_seen:
            visualization.textlog.log_text(f'Sending {self.label}')
            return self.buffer
        return b''  # no change? send nothing.

    def write_received_data_to_memory(self, caller, received_data):
        if received_data:
            consumed = 0
            for addr in self.addresses:
                offset, bank_switch, mem = addr.serializer.unpack_from(received_data, consumed)
                assert offset == addr.target_offset and bank_switch == addr.target_bank
                consumed += addr.serializer.size
                caller.write_memory(offset, mem, bank_switch)
                # also update last_seen so we don't send back something that we just wrote.
                key = (offset, bank_switch)
                self.last_seen[key] = mem
            visualization.textlog.log_text(f'Received {self.label}')
