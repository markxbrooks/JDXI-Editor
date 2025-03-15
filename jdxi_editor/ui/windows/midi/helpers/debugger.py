def _validate_checksum(data_bytes, checksum):
    """Validate Roland SysEx checksum (sum of bytes should be 0 mod 128)"""
    computed_checksum = (128 - (sum(data_bytes) % 128)) % 128
    return computed_checksum == checksum
