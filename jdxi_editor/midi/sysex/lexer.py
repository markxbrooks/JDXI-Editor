import re

from jdxi_editor.midi.data.address.address_map import PARAMETER_ADDRESS_MAP

# Define token patterns
TOKENS = {
    "4-byte-addresses": r"(?:[0-9A-F]{2} ){3}[0-9A-F]{2}",  # 4-byte
    "3-byte-offsets": r"(?:[0-9A-F]{2} ){2}[0-9A-F]{2}",    # 3-byte
}


# Define the mapping (could be loaded dynamically)
TEST_PARAMETER_ADDRESS_MAP = {
    "Temporary Tone": {
        "4-byte-addresses": {
            "18 00 00 00": "Temporary Program",
            "19 00 00 00": "Temporary Tone (Digital Synth Part 1)",
            "19 20 00 00": "Temporary Tone (Digital Synth Part 2)",
            "19 40 00 00": "Temporary Tone (Analog Synth Part)",
            "19 60 00 00": "Temporary Tone (Drums Part)"
        },
        "3-byte-offsets": {
            "01 00 00": "Temporary SuperNATURAL Synth Tone",
            "02 00 00": "Temporary Analog Synth Tone",
            "10 00 00": "Temporary Drum Kit"
        }
    }
}


# Lexing function
def lex_addresses(input_data: str):
    tokens = []
    used = set()

    # First extract 4-byte addresses
    pattern_4 = TOKENS["4-byte-addresses"]
    for match in re.findall(pattern_4, input_data):
        normalized = ' '.join(match.split())
        tokens.append(("4-byte-addresses", normalized))
        used.add(normalized)

    # Then extract 3-byte offsets, skipping ones already covered
    pattern_3 = TOKENS["3-byte-offsets"]
    for match in re.findall(pattern_3, input_data):
        normalized = ' '.join(match.split())
        if not any(normalized in used_address for used_address in used):
            tokens.append(("3-byte-offsets", normalized))

    return tokens


# Map tokens dynamically
def map_tokens_all(tokens):
    mapped_results = {}
    for token_type, token_value in tokens:
        found = False
        for category, types in TEST_PARAMETER_ADDRESS_MAP.items():
            token_map = types.get(token_type, {})
            if token_value in token_map:
                mapped_results[token_value] = f"{token_map[token_value]} [{category}]"
                found = True
                break
        if not found:
            mapped_results[token_value] = "Unknown"
    return mapped_results


if __name__ == "__main__":
    """
    Expected output:
    18 00 00 00 -> Temporary Program
    19 00 00 00 -> Temporary Tone (Digital Synth Part 1)
    01 00 00 -> Temporary SuperNATURAL Synth Tone
    19 20 00 00 -> Temporary Tone (Digital Synth Part 2)
    10 00 00 -> Temporary Drum Kit
    """

    # Example input data
    input_data = """
    18 00 00 00
    19 00 00 00
    01 00 00
    19 20 00 00
    10 00 00
    """

    # Lexing and mapping
    tokens = lex_addresses(input_data)
    mapped = map_tokens_all(tokens)

    for address, description in mapped.items():
        print(f"{address} -> {description}")

