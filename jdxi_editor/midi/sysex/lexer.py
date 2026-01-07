import re

from jdxi_editor.midi.data.address.address import (
    AddressOffsetProgramLMB,
    AddressOffsetSuperNATURALLMB,
    AddressOffsetSystemLMB,
    AddressOffsetTemporaryToneUMB,
    AddressStartMSB,
)

# Define token patterns
TOKENS = {
    "4-byte-addresses": r"(?:[0-9A-F]{2} ){3}[0-9A-F]{2}",  # 4-byte
    "3-byte-offsets": r"(?:[0-9A-F]{2} ){2}[0-9A-F]{2}",  # 3-byte
}


# Define the mapping (could be loaded dynamically)
TEST_PARAMETER_ADDRESS_MAP = {
    "System": {
        "4-byte-addresses": {
            "01 00 00 00": AddressStartMSB.SETUP.name,  # "Setup",
            "02 00 00 00": AddressStartMSB.SYSTEM.name,  # "System"
        },
        "3-byte-offsets": {
            "00 00 00": AddressOffsetSystemLMB.COMMON.name,  # "System Common",
            "00 03 00": AddressOffsetSystemLMB.CONTROLLER.name,  # "System Controller"
        },
    },
    "Temporary Tone": {
        "4-byte-addresses": {
            "18 00 00 00": AddressStartMSB.TEMPORARY_PROGRAM.name,  # Temporary Program
            "19 00 00 00": AddressOffsetTemporaryToneUMB.DIGITAL_SYNTH_1.name,  # "Temporary Tone (Digital Synth Part 1)",
            "19 20 00 00": AddressOffsetTemporaryToneUMB.DIGITAL_SYNTH_2.name,  # "Temporary Tone (Digital Synth Part 2)",
            "19 40 00 00": AddressOffsetTemporaryToneUMB.ANALOG_SYNTH.name,  # "Temporary Tone (Analog Synth Part)",
            "19 60 00 00": AddressOffsetTemporaryToneUMB.DRUM_KIT.name,  # "Temporary Tone (Drums Part)"
        },
        "3-byte-offsets": {
            "01 00 00": AddressOffsetTemporaryToneUMB.DIGITAL_SYNTH_1.name,  # "Temporary SuperNATURAL Synth Tone",
            "02 00 00": AddressOffsetTemporaryToneUMB.ANALOG_SYNTH.name,  #  "Temporary Analog Synth T one",
            "10 00 00": AddressOffsetTemporaryToneUMB.DRUM_KIT.name,  #  "Temporary Drum Kit"
        },
    },
    "Program": {
        "3-byte-offsets": {
            "00 00 00": AddressOffsetProgramLMB.COMMON.name,  # "Program Common",
            "00 01 00": AddressOffsetProgramLMB.VOCAL_EFFECT.name,  # "Program Vocal Effect",
            "00 02 00": AddressOffsetProgramLMB.EFFECT_1.name,  # "Program Effect 1",
            "00 04 00": AddressOffsetProgramLMB.EFFECT_2.name,  # "Program Effect 2",
            "00 06 00": AddressOffsetProgramLMB.DELAY.name,  # "Program Delay",
            "00 08 00": AddressOffsetProgramLMB.REVERB.name,  # "Program Reverb",
            "00 20 00": AddressOffsetProgramLMB.PART_DIGITAL_SYNTH_1.name,  # "Program Part (Digital Synth Part 1)",
            "00 21 00": AddressOffsetProgramLMB.PART_DIGITAL_SYNTH_2.name,  # "Program Part (Digital Synth Part 2)",
            "00 22 00": AddressOffsetProgramLMB.PART_ANALOG.name,  # "Program Part (Analog Synth Part)",
            "00 23 00": AddressOffsetProgramLMB.PART_DRUM.name,  # "Program Part (Drums Part)",
            "00 30 00": AddressOffsetProgramLMB.ZONE_DIGITAL_SYNTH_1.name,  # "Program Zone (Digital Synth Part 1)",
            "00 31 00": AddressOffsetProgramLMB.ZONE_DIGITAL_SYNTH_2.name,  # "Program Zone (Digital Synth Part 2)",
            "00 32 00": AddressOffsetProgramLMB.ZONE_ANALOG.name,  # "Program Zone (Analog Synth Part)",
            "00 33 00": AddressOffsetProgramLMB.ZONE_DRUM.name,  # "Program Zone (Drums Part)",
            "00 40 00": AddressOffsetProgramLMB.CONTROLLER.name,
        }
    },
    "SuperNATURAL Synth Tone": {
        "3-byte-offsets": {
            "00 00 00": AddressOffsetSuperNATURALLMB.COMMON.name,  # "SuperNATURAL Synth Tone Common",
            "00 20 00": AddressOffsetSuperNATURALLMB.PARTIAL_1.name,  # "SuperNATURAL Synth Tone Partial (1)",
            "00 21 00": AddressOffsetSuperNATURALLMB.PARTIAL_2.name,  # "SuperNATURAL Synth Tone Partial (2)",
            "00 22 00": AddressOffsetSuperNATURALLMB.PARTIAL_3.name,  # "SuperNATURAL Synth Tone Partial (3)",
            "00 50 00": AddressOffsetSuperNATURALLMB.MODIFY.name,  # "SuperNATURAL Synth Tone Modify"
        }
    },
    "Analog Synth Tone": {
        "3-byte-offsets": {
            "00 00 00": AddressOffsetProgramLMB.COMMON.name  # "Analog Synth Tone"
        }
    },
}


def lex_addresses(input_data: str):
    tokens = []
    used = set()

    # First extract 4-byte addresses
    pattern_4 = TOKENS["4-byte-addresses"]
    for match in re.findall(pattern_4, input_data):
        normalized = " ".join(match.split())
        tokens.append(("4-byte-addresses", normalized))
        used.add(normalized)

        # Extract possible trailing 3-byte offset
        parts = normalized.split()
        offset_candidate = " ".join(parts[1:])  # last 3 bytes
        if offset_candidate not in used:
            tokens.append(("3-byte-offsets", offset_candidate))
            used.add(offset_candidate)

    # Then extract 3-byte offsets not already used
    pattern_3 = TOKENS["3-byte-offsets"]
    for match in re.findall(pattern_3, input_data):
        normalized = " ".join(match.split())
        if normalized not in used:
            tokens.append(("3-byte-offsets", normalized))
            used.add(normalized)

    return tokens


# Map tokens dynamically
def map_tokens_all(tokens):
    mapped_results = {}
    for token_type, token_value in tokens:
        found = False
        for temporary_area, types in TEST_PARAMETER_ADDRESS_MAP.items():
            token_map = types.get(token_type, {})
            if token_value in token_map:
                mapped_results[token_value] = (
                    f"{token_map[token_value]} [{temporary_area}]"
                )
                found = True
                break
        if not found:
            mapped_results[token_value] = "Unknown"
    return mapped_results


if __name__ == "__main__":
    """
    Expected output:
    19 20 00 00 -> DIGITAL_SYNTH_2 [Temporary Tone] PARTIAL_1 [synth tone]
    """

    # Example input data
    input_data = """
    19 01 20 00
    """

    # Lexing and mapping
    tokens = lex_addresses(input_data)
    mapped = map_tokens_all(tokens)

    for address, temporary_area in mapped.items():
        print(f"{address} -> {temporary_area}")
