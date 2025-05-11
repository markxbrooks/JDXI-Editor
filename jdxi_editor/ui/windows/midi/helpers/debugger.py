def validate_checksum(data_bytes, checksum):
    """Validate Roland SysEx checksum (sum of bytes should be 0 mod 128)"""
    computed_checksum = (128 - (sum(data_bytes) % 128)) % 128
    return computed_checksum == checksum
    
def validate_checksum(data_bytes, checksum):
    # Verify checksum
    data_sum = sum(message[8:-2]) & 0x7F  # Sum from area to value
    checksum = (128 - data_sum) & 0x7F
    if message[-2] != checksum:
        log_message(f"Invalid checksum: expected {checksum}, got {message[-2]}")
        return False