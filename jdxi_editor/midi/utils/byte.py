def split_value_to_nibbles(value: int, size: int = 4):
    """Handle bit value list with variable byte size."""
    try:
        # Ensure size is valid
        if size not in (1, 4, 5):
            raise ValueError("Size must be 1, 4, or 5 bytes.")
        # Prepare an array to hold the bytes
        byte_array = []
        # Process bits based on the specified size
        for i in range(size):
            byte = (value >> (4 * (size - 1 - i))) & 0x0F  # Extract 4 bits
            byte_array.append(byte)
        return byte_array
    except Exception as ex:
        print(f"Error: {ex}")
