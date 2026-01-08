from dataclasses import dataclass


@dataclass
class BitValue:
    size: int  # The number of bits

    @property
    def max(self):
        return self.max_for_size(self.size)

    @staticmethod
    def max_for_size(size: int) -> int:
        """
        Calculates or retrieves the maximum value based on a given bit size using a lookup.
        """
        size_map = {
            4: 0x0F,  # 15, 4-bit max
            7: 0x7F,  # 127, 7-bit max
            8: 0xFF,  # 255, 8-bit max
            14: 0x3FFF,  # 16383, 14-bit max
            16: 0xFFFF,  # 65535, 16-bit max
            32: 0xFFFFFFFF,  # 4294967295, 32-bit max
        }
        return size_map.get(
            size, (1 << size) - 1
        )  # Default to dynamic calc if not in map
