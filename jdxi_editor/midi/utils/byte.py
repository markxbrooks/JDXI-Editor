def split_value_to_nibbles(value: int) -> list[int]:
    """Splits an integer into exactly 4 nibbles (4-bit values), padding with zeros if necessary."""
    if value < 0:
        raise ValueError("Value must be a non-negative integer.")

    nibbles = []
    for i in range(4):
        nibbles.append((value >> (4 * (3 - i))) & 0x0F)  # Extract 4 bits per iteration

    return nibbles  # Always returns a 4-element list
