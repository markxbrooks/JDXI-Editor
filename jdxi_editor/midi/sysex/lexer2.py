import re

from jdxi_editor.midi.data.address.address import (
    AddressOffsetProgramLMB,
    AddressOffsetSuperNATURALLMB,
    AddressOffsetSystemLMB,
    AddressOffsetSystemUMB,
    AddressOffsetTemporaryToneUMB,
    AddressStartMSB,
)

# Simplified token matchers
TOKENS = {
    "4-byte-addresses": r"(?:[0-9A-F]{2} ){3}[0-9A-F]{2}",
    "3-byte-offsets": r"(?:[0-9A-F]{2} ){2}[0-9A-F]{2}",
}

# Your test mapping
TEST_PARAMETER_ADDRESS_MAP = {
    "System": {
        "4-byte-addresses": {
            "01 00 00 00": AddressStartMSB.SETUP.name,
            "02 00 00 00": AddressStartMSB.SYSTEM.name,
        },
        "3-byte-offsets": {
            "00 00 00": AddressOffsetSystemUMB.COMMON.name,
            "00 03 00": AddressOffsetSystemLMB.CONTROLLER.name,
        },
    },
    "Temporary Tone": {
        "4-byte-addresses": {
            "18 00 00 00": AddressStartMSB.TEMPORARY_PROGRAM.name,
            "19 00 00 00": AddressOffsetTemporaryToneUMB.DIGITAL_SYNTH_1.name,
            "19 20 00 00": AddressOffsetTemporaryToneUMB.DIGITAL_SYNTH_2.name,
            "19 40 00 00": AddressOffsetTemporaryToneUMB.ANALOG_SYNTH.name,
            "19 60 00 00": AddressOffsetTemporaryToneUMB.DRUM_KIT.name,
        },
        "3-byte-offsets": {
            "01 00 00": AddressOffsetTemporaryToneUMB.DIGITAL_SYNTH_1.name,
            "02 00 00": AddressOffsetTemporaryToneUMB.ANALOG_SYNTH.name,
            "10 00 00": AddressOffsetTemporaryToneUMB.DRUM_KIT.name,
        },
    },
    "Program": {
        "3-byte-offsets": {
            "00 00 00": AddressOffsetProgramLMB.COMMON.name,
            "00 01 00": AddressOffsetProgramLMB.VOCAL_EFFECT.name,
            "00 02 00": AddressOffsetProgramLMB.EFFECT_1.name,
            "00 04 00": AddressOffsetProgramLMB.EFFECT_2.name,
            "00 06 00": AddressOffsetProgramLMB.DELAY.name,
            "00 08 00": AddressOffsetProgramLMB.REVERB.name,
            "00 20 00": AddressOffsetProgramLMB.PART_DIGITAL_SYNTH_1.name,
            "00 21 00": AddressOffsetProgramLMB.PART_DIGITAL_SYNTH_2.name,
            "00 22 00": AddressOffsetProgramLMB.PART_ANALOG.name,
            "00 23 00": AddressOffsetProgramLMB.PART_DRUM.name,
            "00 30 00": AddressOffsetProgramLMB.ZONE_DIGITAL_SYNTH_1.name,
            "00 31 00": AddressOffsetProgramLMB.ZONE_DIGITAL_SYNTH_2.name,
            "00 32 00": AddressOffsetProgramLMB.ZONE_ANALOG.name,
            "00 33 00": AddressOffsetProgramLMB.ZONE_DRUM.name,
            "00 40 00": AddressOffsetProgramLMB.CONTROLLER.name,
        }
    },
    "SuperNATURAL Synth Tone": {
        "3-byte-offsets": {
            "00 00 00": AddressOffsetSuperNATURALLMB.COMMON.name,
            "00 20 00": AddressOffsetSuperNATURALLMB.PARTIAL_1.name,
            "00 21 00": AddressOffsetSuperNATURALLMB.PARTIAL_2.name,
            "00 22 00": AddressOffsetSuperNATURALLMB.PARTIAL_3.name,
            "00 50 00": AddressOffsetSuperNATURALLMB.MODIFY.name,
        }
    },
    "Analog Synth Tone": {
        "3-byte-offsets": {
            "00 00 00": AddressOffsetProgramLMB.COMMON.name,
        }
    },
}


def lex_addresses(input_data: str):
    tokens = []
    used = set()

    # Match 4-byte addresses
    for match in re.findall(TOKENS["4-byte-addresses"], input_data):
        normalized = " ".join(match.split())
        tokens.append(("4-byte-addresses", normalized))
        used.add(normalized)

        # Also extract implied 3-byte offset
        parts = normalized.split()
        if len(parts) == 4:
            offset = " ".join(parts[1:])
            if offset not in used:
                tokens.append(("3-byte-offsets", offset))
                used.add(offset)

    # Match any remaining 3-byte offsets
    for match in re.findall(TOKENS["3-byte-offsets"], input_data):
        normalized = " ".join(match.split())
        if normalized not in used:
            tokens.append(("3-byte-offsets", normalized))
            used.add(normalized)

    return tokens


def map_tokens_all(tokens):
    mapped = {}

    for token_type, token_value in tokens:
        matched = False

        if token_type == "4-byte-addresses":
            token_value.split()[0]
            offset = " ".join(token_value.split()[1:])

            for area_name, entry in TEST_PARAMETER_ADDRESS_MAP.items():
                if token_value in entry.get("4-byte-addresses", {}):
                    mapped[token_value] = (
                        f"{entry['4-byte-addresses'][token_value]} [{area_name}]"
                    )
                    matched = True
                    break

                # If no direct match, try 3-byte offset under same area
                if offset in entry.get("3-byte-offsets", {}):
                    mapped[token_value] = (
                        f"{entry['3-byte-offsets'][offset]} [offset of {area_name}]"
                    )
                    matched = True
                    break

        elif token_type == "3-byte-offsets":
            for area_name, entry in TEST_PARAMETER_ADDRESS_MAP.items():
                if token_value in entry.get("3-byte-offsets", {}):
                    mapped[token_value] = (
                        f"{entry['3-byte-offsets'][token_value]} [{area_name}]"
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
    00 22 00
    00 03 00
    """

    tokens = lex_addresses(input_data)
    mapped = map_tokens_all(tokens)

    for addr, label in mapped.items():
        print(f"{addr} -> {label}")
