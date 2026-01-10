import re
from jdxi_editor.midi.data.address.address_map import PARAMETER_ADDRESS_MAP
from picomidi.core.parameter.factory import AddressFactory
from picomidi.core.parameter.kind import ByteGroupKind

# Simplified token matchers
TOKENS = {
    ByteGroupKind.ADDRESS_4: r"(?:[0-9A-F]{2} ){3}[0-9A-F]{2}",
    ByteGroupKind.OFFSET_3: r"(?:[0-9A-F]{2} ){2}[0-9A-F]{2}",
}


def lex_addresses(input_data: str):
    tokens = []
    used = set()

    # Known address MSBs that indicate 4-byte addresses
    known_msbs = {"01", "02", "18", "19"}

    # Match 4-byte addresses
    for match in re.findall(TOKENS[ByteGroupKind.ADDRESS_4], input_data):
        normalized = " ".join(match.split())
        tokens.append((ByteGroupKind.ADDRESS_4, normalized))
        used.add(normalized)

        # Also extract implied 3-byte offset
        parts = normalized.split()
        if len(parts) == 4:
            offset = " ".join(parts[1:])
            if offset not in used:
                tokens.append((ByteGroupKind.OFFSET_3, offset))
                used.add(offset)

    # Match any remaining 3-byte offsets, but check if they might be incomplete 4-byte addresses
    for match in re.findall(TOKENS[ByteGroupKind.OFFSET_3], input_data):
        normalized = " ".join(match.split())
        if normalized not in used:
            # Check if this looks like an incomplete 4-byte address (starts with known MSB)
            parts = normalized.split()
            if len(parts) == 3 and parts[0] in known_msbs:
                # Treat as incomplete 4-byte address - pad with 00
                incomplete_address = f"{normalized} 00"
                if incomplete_address not in used:
                    tokens.append((ByteGroupKind.ADDRESS_4, incomplete_address))
                    used.add(incomplete_address)
                    used.add(normalized)  # Mark original as used to avoid duplicate
            else:
                # Valid standalone 3-byte offset
                tokens.append((ByteGroupKind.OFFSET_3, normalized))
                used.add(normalized)

    return tokens


def map_tokens_all(tokens):
    mapped = {}
    matched_offsets = set()  # Track offsets that were matched as part of 4-byte addresses

    for token_type, token_value in tokens:
        matched = False

        if token_type == ByteGroupKind.ADDRESS_4:
            # Convert string to ParameterAddress object for lookup
            try:
                address_obj = AddressFactory.from_str(token_value)
            except (ValueError, AttributeError):
                mapped[token_value] = "Unknown"
                continue

            offset_str = " ".join(token_value.split()[1:])
            offset_obj = None
            if offset_str:
                try:
                    offset_obj = AddressFactory.from_str(offset_str)
                except (ValueError, AttributeError):
                    pass

            # First try direct address match
            for area_name, entry in PARAMETER_ADDRESS_MAP.items():
                address_map = entry.get(ByteGroupKind.ADDRESS_4, {})
                if address_obj in address_map:
                    enum_value = entry[ByteGroupKind.ADDRESS_4][address_obj]
                    mapped[token_value] = (
                        f"{enum_value.name} [{area_name.name}]"
                    )
                    matched = True
                    break

            # If no direct match, try to match by MSB (base address) + offset
            if not matched and offset_obj:
                parts = token_value.split()
                if len(parts) == 4:
                    msb = parts[0]
                    # Try to find a base address that matches this MSB
                    base_address_str = f"{msb} 00 00 00"
                    try:
                        base_address_obj = AddressFactory.from_str(base_address_str)
                        # Find which area this base address belongs to
                        base_area = None
                        base_enum = None
                        for area_name, entry in PARAMETER_ADDRESS_MAP.items():
                            address_map = entry.get(ByteGroupKind.ADDRESS_4, {})
                            if base_address_obj in address_map:
                                base_area = area_name
                                base_enum = entry[ByteGroupKind.ADDRESS_4][base_address_obj]
                                break

                        # Now search all areas for the offset (not just base_area)
                        for area_name, entry in PARAMETER_ADDRESS_MAP.items():
                            offset_map = entry.get(ByteGroupKind.OFFSET_3, {})
                            if offset_obj in offset_map:
                                enum_value = entry[ByteGroupKind.OFFSET_3][offset_obj]
                                mapped[token_value] = (
                                    f"{enum_value.name} [{area_name.name}]"
                                )
                                matched = True
                                # Mark this offset as matched so we don't match it separately
                                matched_offsets.add(offset_str)
                                break

                        # If offset not found but we have a base area, show base info
                        if not matched and base_area and base_enum:
                            mapped[token_value] = (
                                f"{base_enum.name} [{base_area.name}] + offset {offset_str} (unknown)"
                            )
                            matched = True
                            # Mark this offset as matched so we don't match it separately
                            matched_offsets.add(offset_str)
                    except (ValueError, AttributeError):
                        pass

        elif token_type == ByteGroupKind.OFFSET_3:
            # Skip if this offset was already matched as part of a 4-byte address
            if token_value in matched_offsets:
                continue

            # Convert string to ParameterOffset object for lookup
            try:
                offset_obj = AddressFactory.from_str(token_value)
            except (ValueError, AttributeError):
                mapped[token_value] = "Unknown"
                continue

            for area_name, entry in PARAMETER_ADDRESS_MAP.items():
                offset_map = entry.get(ByteGroupKind.OFFSET_3, {})
                if offset_obj in offset_map:
                    enum_value = entry[ByteGroupKind.OFFSET_3][offset_obj]
                    mapped[token_value] = (
                        f"{enum_value.name} [{area_name.name}]"
                    )
                    matched = True
                    break

        if not matched:
            mapped[token_value] = "Unknown"

    return mapped


if __name__ == "__main__":
    input_data = """
    19 01 20 00
    19 01 20 00
    19 00 22 00
    18 00 03 00
    """

    tokens = lex_addresses(input_data)
    mapped = map_tokens_all(tokens)

    for addr, label in mapped.items():
        print(f"{addr} -> {label}")
