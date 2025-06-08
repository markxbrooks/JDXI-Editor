from jdxi_editor.log.logger import Logger as log


def validate_checksum(data_bytes: bytes, checksum: int) -> bool:
    """
    Validate Roland SysEx checksum (sum of bytes should be 0 mod 128)
    :param data_bytes: bytes
    :param checksum: int
    :return: bool True on success, False otherwise
    """
    computed_checksum = (128 - (sum(data_bytes) % 128)) % 128
    if computed_checksum != checksum:
        log.message(f"Invalid checksum: expected {computed_checksum}, got {checksum}")
        return False
    return True
