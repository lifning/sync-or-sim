from sync.primitives import IStrategy, MirroredAddress
import visualization.textlog


class SimpleOnChangeStrategy(IStrategy):
    """
    A strategy that watches emulator memory & sends it when a change is detected
    and applies data immediately when it is received (before collecting data to send)
    """
    def __init__(self, offset_length_pairs, label):
        super().__init__()
        self.addresses = [MirroredAddress(x[1], x[0], source_bank=(x[2] if len(x) > 2 else 0))
                          if isinstance(x, tuple) else x
                          for x in offset_length_pairs]
        self.buffer_size = sum(x.serializer.size for x in self.addresses)
        self.buffer = bytearray(self.buffer_size)
        self.label = label
        self.last_seen = {}  # store synchronized received memory & keep track of memory we have sent
        self.received_unsynced = {}  # store unsynchronized received memory


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
                                      addr.target_offset, addr.target_bank, addr.should_write, block)
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
                offset, bank_switch, should_write, mem = addr.serializer.unpack_from(received_data, consumed)
                assert offset == addr.target_offset and bank_switch == addr.target_bank
                consumed += addr.serializer.size
                key = (offset, bank_switch)
                if should_write:
                    old = self.last_seen.get(key)
                    if old is not None:
                        assert len(old) == len(mem)
                        mem, extra = addr.update_fn(old, mem)
                    caller.write_memory(offset, mem, bank_switch)
                    # also update last_seen so we don't send back something that we just wrote.
                    self.last_seen[key] = mem
                else:
                    self.received_unsynced[key] = mem
            visualization.textlog.log_text(f'Received {self.label}')

    def get_last_received_value(self, offset, length, bank_switch=0):
        value = self._get_value_from_received_map(self.received_unsynced, offset, length, bank_switch)
        if value is None:
            value = self._get_value_from_received_map(self.last_seen, offset, length, bank_switch)
        return value

    def _get_value_from_received_map(self, received_map, offset, length, bank_switch):
        for received_map_range in received_map.keys():
            if bank_switch == received_map_range[1] and offset >= received_map_range[0]:
                # bank and start offset matches, figure out what the end offset is of the requested region
                end_offset = offset + length
                received_map_range_end_offset = received_map_range[0] + len(received_map[received_map_range])

                if end_offset <= received_map_range_end_offset:
                    # figure out internal offset
                    internal_offset = offset - received_map_range[0]
                    return received_map[received_map_range][internal_offset:internal_offset + length]
        return None
