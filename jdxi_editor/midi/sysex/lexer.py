import re

# Define token patterns
TOKENS = {
    "4-byte-address": r"([0-9A-F]{2} ){3}[0-9A-F]{2}",  # Matches patterns like "19 00 00 00"
    "3-byte-offset": r"([0-9A-F]{2} ){2}[0-9A-F]{2}",   # Matches patterns like "01 00 00"
}

# Define the mapping (could be loaded dynamically)
ADDRESS_DESCRIPTION_MAP = {
    "Temporary Tone": {
        "4-byte-address": {
            "18 00 00 00": "Temporary Program",
            "19 00 00 00": "Temporary Tone (Digital Synth Part 1)",
            "19 20 00 00": "Temporary Tone (Digital Synth Part 2)",
            "19 40 00 00": "Temporary Tone (Analog Synth Part)",
            "19 60 00 00": "Temporary Tone (Drums Part)"
        },
        "3-byte-offset": {
            "01 00 00": "Temporary SuperNATURAL Synth Tone",
            "02 00 00": "Temporary Analog Synth Tone",
            "10 00 00": "Temporary Drum Kit"
        }
    }
}

# Lexing function
def lex_addresses(input_data: str):
    tokens = []
    for token_type, pattern in TOKENS.items():
        matches = re.findall(pattern, input_data)
        for match in matches:
            tokens.append((token_type, match.strip()))
    return tokens

# Map tokens dynamically
def map_tokens(tokens, category):
    mapped_results = {}
    for token_type, token_value in tokens:
        description = ADDRESS_DESCRIPTION_MAP.get(category, {}).get(token_type, {}).get(token_value, "Unknown")
        mapped_results[token_value] = description
    return mapped_results

# Example input data
input_data = """
18 00 00 00
19 00 00 00
01 00 00
19 20 00 00
10 00 00
"""

18 00 00 00 -> Temporary Program
19 00 00 00 -> Temporary Tone (Digital Synth Part 1)
01 00 00 -> Temporary SuperNATURAL Synth Tone
19 20 00 00 -> Temporary Tone (Digital Synth Part 2)
10 00 00 -> Temporary Drum Kit

# Lexing and mapping
tokens = lex_addresses(input_data)
mapped = map_tokens(tokens, "Temporary Tone")

# Print results
for address, description in mapped.items():
    print(f"{address} -> {description}")