#!/usr/bin/env python3
"""
Script to parse SysEx hex strings from JD-Xi and save as JSON.

Usage:
    python3 parse_sysex_hex.py <hex_string> [output_file]
    
Or provide multiple hex strings as separate arguments.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from jdxi_editor.midi.sysex.parser.sysex import JDXiSysExParser
from jdxi_editor.log.logger import Logger as log


def hex_string_to_bytes(hex_string: str) -> bytes:
    """
    Convert a hex string (with or without spaces) to bytes.
    
    :param hex_string: str Hex string like "F0 41 10 ..." or "F04110..."
    :return: bytes
    """
    # Remove spaces and convert to bytes
    hex_clean = hex_string.replace(" ", "").replace("\n", "").replace("\r", "")
    return bytes.fromhex(hex_clean)


def parse_sysex_hex(hex_string: str) -> Dict[str, Any] | None:
    """
    Parse a SysEx hex string and return the parsed data.
    
    :param hex_string: str Hex string representation of SysEx message
    :return: dict Parsed SysEx data or None if parsing fails
    """
    try:
        sysex_bytes = hex_string_to_bytes(hex_string)
        parser = JDXiSysExParser()
        parsed_data = parser.parse_bytes(sysex_bytes)
        return parsed_data
    except Exception as ex:
        log.error(f"Failed to parse SysEx hex: {ex}")
        return None


def parse_multiple_sysex(hex_strings: List[str]) -> List[Dict[str, Any]]:
    """
    Parse multiple SysEx hex strings.
    
    :param hex_strings: List[str] List of hex string representations
    :return: List[dict] List of parsed SysEx data
    """
    parsed_results = []
    for i, hex_str in enumerate(hex_strings, 1):
        log.message(f"Parsing SysEx message {i}/{len(hex_strings)}...")
        parsed = parse_sysex_hex(hex_str)
        if parsed:
            parsed_results.append(parsed)
            address = parsed.get("ADDRESS", "unknown")
            log.message(f"✓ Parsed message {i} - ADDRESS: {address}")
        else:
            log.warning(f"✗ Failed to parse message {i}")
    
    return parsed_results


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python3 parse_sysex_hex.py <hex_string1> [hex_string2] ... [output_file]")
        print("\nExample:")
        print('  python3 parse_sysex_hex.py "F0 41 10 00 00 00 0E 12 18 00 00 00 ... F7"')
        sys.exit(1)
    
    # Check if last argument is an output file (ends with .json)
    args = sys.argv[1:]
    output_file = None
    if len(args) > 1 and args[-1].endswith('.json'):
        output_file = Path(args[-1])
        hex_strings = args[:-1]
    else:
        hex_strings = args
        output_file = Path.home() / "jdxi_parsed_sysex.json"
    
    log.header_message(f"Parsing {len(hex_strings)} SysEx message(s)...")
    
    # Parse all hex strings
    parsed_results = parse_multiple_sysex(hex_strings)
    
    if not parsed_results:
        log.error("No SysEx messages were successfully parsed.")
        return 1
    
    # Prepare output data
    output_data = {
        "total_messages": len(parsed_results),
        "messages": parsed_results
    }
    
    # Save to file
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        log.header_message(f"✓ Successfully parsed {len(parsed_results)} SysEx message(s)")
        log.message(f"Output file: {output_file}")
        
        # Show summary
        addresses = [msg.get("ADDRESS", "unknown") for msg in parsed_results]
        log.message(f"Parsed addresses: {', '.join(set(addresses))}")
        
        return 0
    except Exception as ex:
        log.error(f"Failed to save output: {ex}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

