#!/usr/bin/env python3
"""
Parse the SysEx responses from Program F18 that were captured.

This script parses the hex strings provided and saves them as JSON.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from decologr import Decologr as log

from jdxi_editor.midi.sysex.parser.sysex import JDXiSysExParser


def hex_string_to_bytes(hex_string: str) -> bytes:
    """Convert hex string to bytes."""
    hex_clean = hex_string.replace(" ", "").replace("\n", "").replace("\r", "")
    return bytes.fromhex(hex_clean)


def parse_sysex_hex(hex_string: str) -> Dict[str, Any] | None:
    """Parse a SysEx hex string."""
    try:
        sysex_bytes = hex_string_to_bytes(hex_string)
        parser = JDXiSysExParser()
        parsed_data = parser.parse_bytes(sysex_bytes)
        return parsed_data
    except Exception as ex:
        log.error(f"Failed to parse SysEx: {ex}")
        return None


def main():
    """Parse Program F18 SysEx responses."""
    
    # SysEx messages from Program F18 (excluding the Universal Non-Real Time message)
    sysex_messages = [
        # Program Common
        "F0 41 10 00 00 00 0E 12 18 00 00 00 43 45 52 45 4D 4F 4E 59 20 20 20 20 20 20 20 20 78 01 0D 0B 00 00 00 01 01 01 01 00 00 00 00 00 00 00 00 00 71 F7",
        
        # Analog Synth
        "F0 41 10 00 00 00 0E 12 19 42 00 00 48 6F 75 73 65 20 42 61 73 73 20 31 00 01 37 00 00 11 40 40 40 01 02 40 40 00 7F 40 7F 7F 40 01 01 7F 40 00 40 00 0A 1E 00 7F 5C 40 5E 00 7F 00 00 00 14 00 40 00 02 00 50 40 40 52 00 00 00 00 05 F7",
        
        # Drum Kit
        "F0 41 10 00 00 00 0E 12 19 70 00 00 37 30 37 26 37 32 37 20 4B 69 74 31 7F 00 00 00 00 0D 0E F7",
        
        # Digital Synth 1 Common
        "F0 41 10 00 00 00 0E 12 19 01 00 00 46 69 6E 67 65 72 64 20 42 73 20 31 72 00 07 08 00 00 00 14 00 40 00 00 00 01 01 00 00 00 00 00 00 00 00 00 18 01 00 00 00 00 01 00 00 00 00 00 00 01 01 01 00 00 15 00 00 00 00 40 03 40 40 40 75 F7",
        
        # Digital Synth 1 Partial 1
        "F0 41 10 00 00 00 0E 12 19 01 20 00 07 00 00 40 40 7F 00 7F 7F 40 01 00 7F 40 68 00 00 7F 00 3C 77 64 53 00 64 00 05 40 00 51 00 11 00 00 40 40 40 40 00 50 00 11 7F 00 4C 40 40 40 49 4A 40 40 03 00 00 08 07 00 00 52 40 43 F7",
        
        # Digital Synth 1 Partial 2
        "F0 41 10 00 00 00 0E 12 19 01 21 00 01 00 00 40 40 7F 00 7F 7F 40 01 01 7F 40 40 00 00 24 00 00 40 64 53 00 00 7F 00 40 00 51 00 11 00 00 40 40 40 40 00 58 00 11 7F 00 50 40 40 40 49 4A 40 40 01 00 00 00 0E 00 00 52 40 1E F7",
        
        # Digital Synth 1 Partial 3
        "F0 41 10 00 00 00 0E 12 19 01 22 00 07 00 00 40 40 7F 00 7F 7F 40 01 01 7F 40 40 00 00 24 00 00 40 64 53 00 00 7F 00 40 00 51 00 11 00 00 40 40 40 40 00 58 00 11 7F 00 50 40 40 40 49 4A 40 40 01 00 00 00 0E 00 00 52 40 17 F7",
        
        # Digital Synth 1 Modify
        "F0 41 10 00 00 00 0E 12 19 01 50 00 07 00 00 00 00 0B 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 04 F7",
        
        # Digital Synth 2 Common (same as Digital 1, appears twice in the capture)
        "F0 41 10 00 00 00 0E 12 18 00 00 00 43 45 52 45 4D 4F 4E 59 20 20 20 20 20 20 20 20 78 01 0D 0B 00 00 00 01 01 01 01 00 00 00 00 00 00 00 00 00 71 F7",
        
        # Digital Synth 2 Analog (same as Digital 1)
        "F0 41 10 00 00 00 0E 12 19 42 00 00 48 6F 75 73 65 20 42 61 73 73 20 31 00 01 37 00 00 11 40 40 40 01 02 40 40 00 7F 40 7F 7F 40 01 01 7F 40 00 40 00 0A 1E 00 7F 5C 40 5E 00 7F 00 00 00 14 00 40 00 02 00 50 40 40 52 00 00 00 00 05 F7",
        
        # Digital Synth 2 Drum (same as Digital 1)
        "F0 41 10 00 00 00 0E 12 19 70 00 00 37 30 37 26 37 32 37 20 4B 69 74 31 7F 00 00 00 00 0D 0E F7",
        
        # Digital Synth 2 Common
        "F0 41 10 00 00 00 0E 12 19 01 00 00 46 69 6E 67 65 72 64 20 42 73 20 31 72 00 07 08 00 00 00 14 00 40 00 00 00 01 01 00 00 00 00 00 00 00 00 00 18 01 00 00 00 00 01 00 00 00 00 00 00 01 01 01 00 00 15 00 00 00 00 40 03 40 40 40 75 F7",
        
        # Digital Synth 2 Partial 1
        "F0 41 10 00 00 00 0E 12 19 01 20 00 07 00 00 40 40 7F 00 7F 7F 40 01 00 7F 40 68 00 00 7F 00 3C 77 64 53 00 64 00 05 40 00 51 00 11 00 00 40 40 40 40 00 50 00 11 7F 00 4C 40 40 40 49 4A 40 40 03 00 00 08 07 00 00 52 40 43 F7",
        
        # Digital Synth 2 Partial 2
        "F0 41 10 00 00 00 0E 12 19 01 21 00 01 00 00 40 40 7F 00 7F 7F 40 01 01 7F 40 40 00 00 24 00 00 40 64 53 00 00 7F 00 40 00 51 00 11 00 00 40 40 40 40 00 58 00 11 7F 00 50 40 40 40 49 4A 40 40 01 00 00 00 0E 00 00 52 40 1E F7",
        
        # Digital Synth 2 Partial 3
        "F0 41 10 00 00 00 0E 12 19 01 22 00 07 00 00 40 40 7F 00 7F 7F 40 01 01 7F 40 40 00 00 24 00 00 40 64 53 00 00 7F 00 40 00 51 00 11 00 00 40 40 40 40 00 58 00 11 7F 00 50 40 40 40 49 4A 40 40 01 00 00 00 0E 00 00 52 40 17 F7",
        
        # Digital Synth 2 Modify
        "F0 41 10 00 00 00 0E 12 19 01 50 00 07 00 00 00 00 0B 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 04 F7",
    ]
    
    output_file = Path.home() / "jdxi_program_f18_parsed.json"
    
    log.header_message(f"Parsing {len(sysex_messages)} SysEx messages from Program F18...")
    
    parsed_results = []
    for i, hex_str in enumerate(sysex_messages, 1):
        log.message(f"Parsing message {i}/{len(sysex_messages)}...")
        parsed = parse_sysex_hex(hex_str)
        if parsed:
            parsed_results.append(parsed)
            address = parsed.get("ADDRESS", "unknown")
            temporary_area = parsed.get("TEMPORARY_AREA", "unknown")
            synth_tone = parsed.get("SYNTH_TONE", "unknown")
            log.message(f"✓ Parsed message {i} - ADDRESS: {address}, AREA: {temporary_area}, TONE: {synth_tone}")
        else:
            log.warning(f"✗ Failed to parse message {i}")
    
    if not parsed_results:
        log.error("No messages were successfully parsed.")
        return 1
    
    # Prepare output data
    output_data = {
        "program": "F18",
        "bank": "F",
        "program_number": 18,
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
        unique_addresses = set(addresses)
        log.message(f"Parsed addresses ({len(unique_addresses)} unique): {', '.join(sorted(unique_addresses))}")
        
        return 0
    except Exception as ex:
        log.error(f"Failed to save output: {ex}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

