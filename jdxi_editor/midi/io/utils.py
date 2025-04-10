"""
utility functions 

"""


def format_midi_message_to_hex_string(message):
    """hexlify message"""
    formatted_message = " ".join([hex(x)[2:].upper().zfill(2) for x in message])
    return formatted_message


def construct_address(area, group, param, part):
    """Address construction"""
    address = [area, part, group & 0xFF, param & 0xFF]
    return address


def increment_group(group, param):
    """Adjust group if param exceeds 127"""
    if param > 127:
        group += 1
    return group
