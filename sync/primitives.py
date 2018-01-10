import struct


g_ushort_struct = struct.Struct('<H')


class IGameSync:
    def __init__(self, read_memory_callback, write_memory_callback):
        self.read_memory = read_memory_callback
        self.write_memory = write_memory_callback
        self.strats = []

    # return any data that should be sent from this step
    def on_emulator_step(self, received_data):
        updates = []
        blocks = self._unpack_blocks(received_data)
        for strat_id in range(len(self.strats)):
            update = self.strats[strat_id].on_emulator_step(self, blocks.get(strat_id))
            if update:
                updates.append(g_ushort_struct.pack(strat_id))
                updates.append(update)
        return b''.join(updates)

    def _unpack_blocks(self, received_data):
        consumed = 0
        blocks = {}
        while consumed < len(received_data):
            strat_id, = g_ushort_struct.unpack_from(received_data, consumed)
            strat = self.strats[strat_id]
            consumed += g_ushort_struct.size
            end = consumed + strat.buffer_size
            blocks[strat_id] = received_data[consumed:end]
            consumed = end
        return blocks


class IStrategy:
    def __init__(self):
        pass

    def on_emulator_step(self, caller, received_data):
        raise NotImplementedError


class UpdateTypes:
    """
    Reference functions for common update types.
    Parameters: (last observed bytes, incoming bytes)
    Return: (result to write to memory, extra data for UI)
    """
    @staticmethod
    def overwrite(old, new):
        """
        Clobbers old data by copy. Extra data is the changed bits.
        """
        return new, bytes(old[i] ^ new[i] for i in range(len(new)))

    @staticmethod
    def bitwise_or(old, new):
        """
        Only sets new bits, never clears them. Extra data is the newly set bits.
        """
        return (bytes(old[i] | new[i] for i in range(len(new))),
                bytes(~old[i] & new[i] for i in range(len(new))))

    @staticmethod
    def bitwise_and(old, new):
        """
        Only clears bits, never sets them. Extra data is the newly cleared bits.
        """
        return (bytes(old[i] & new[i] for i in range(len(new))),
                bytes(old[i] & ~new[i] for i in range(len(new))))

    @staticmethod
    def fixed_value_fn(value):
        return lambda _, new: value, new


class MirroredAddress:
    def __init__(self, size, source_offset, target_offset=None, source_bank=0,
                 target_bank=None, should_write=True, update_fn=UpdateTypes.overwrite):
        self.size = size
        self.source_offset = source_offset
        self.target_offset = target_offset if target_offset is not None else source_offset
        self.source_bank = source_bank
        self.target_bank = target_bank if target_bank is not None else source_bank
        self.should_write = should_write
        # target offset, target bank, should_write, data
        self.serializer = struct.Struct(f'<LB?{size}s')
        self.update_fn = update_fn

    def legacy_tuple(self):
        return self.source_offset, self.size, self.source_bank
