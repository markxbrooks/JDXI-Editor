"""
Tokeniser for lexing
# Example input
# input_data = "DIGITAL_SYNTH_1 COMMON"
# mapping = generate_mapping(input_data)
# print(mapping)

"""
import re
from typing import Optional

# Define token patterns
TOKEN_PATTERNS = {
    "AREA": r"TEMPORARY_(DIGITAL_SYNTH_\d|ANALOG|DRUM_KIT)_AREA",
    "COMMON": r"COMMON|COMMON|MODIFY|PARTIAL_\d",
}


# Lexer function
def tokenize(input_string: str) -> dict[str, str]:
    """
    tokenize

    :param input_string: str
    :return: dict[str,str] tokens
    """
    tokens = {}
    for token_type, pattern in TOKEN_PATTERNS.items():
        match = re.search(pattern, input_string)
        if match:
            tokens[token_type] = match.group()
    return tokens


# Generate mappings dynamically
def generate_mapping(input_string: str) -> Optional[dict[str, str]]:
    """
    generate_mapping

    :param input_string: str
    :return: Optional[dict[str, str]]
    """
    tokens = tokenize(input_string)
    if "AREA" in tokens and "COMMON" in tokens:
        return {
            "SynthType": f"JDXiSynth.{tokens['AREA'].split('_')[1]}",
            "Parameter": f"AddressParameter{tokens['COMMON'].replace('_', '')}"
        }
    return None
