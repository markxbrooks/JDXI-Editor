import re

# Define token patterns
TOKEN_PATTERNS = {
    "AREA": r"TEMPORARY_(DIGITAL_SYNTH_\d|ANALOG|DRUM_KIT)_AREA",
    "COMMON": r"COMMON|TONE_COMMON|TONE_MODIFY|PARTIAL_\d",
}

# Lexer function
def tokenize(input_string):
    tokens = {}
    for token_type, pattern in TOKEN_PATTERNS.items():
        match = re.search(pattern, input_string)
        if match:
            tokens[token_type] = match.group()
    return tokens

# Generate mappings dynamically
def generate_mapping(input_string):
    tokens = tokenize(input_string)
    if "AREA" in tokens and "COMMON" in tokens:
        return {
            "SynthType": f"JDXiSynth.{tokens['AREA'].split('_')[1]}",
            "Parameter": f"AddressParameter{tokens['COMMON'].replace('_', '')}"
        }
    return None

# Example input
# input_data = "TEMPORARY_DIGITAL_SYNTH_1_AREA TONE_COMMON"
# mapping = generate_mapping(input_data)
# print(mapping)
