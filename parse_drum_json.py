#!/usr/bin/env python3
"""
Script to load and parse a Drum JSON file from .msz using JD-Xi's SysExParser.

Usage:
    python3 parse_drum_json.py [path_to_msz_file] [json_filename]
    
Example:
    python3 parse_drum_json.py tests/ceremony_from_software.msz jdxi_tone_data_19703e00.json
"""

import sys
import zipfile
import json
from pathlib import Path
from typing import Optional, Dict, Any

from jdxi_editor.midi.sysex.parser.json import JDXiJsonSysexParser
from jdxi_editor.log.logger import Logger as log

# Also print directly for visibility
def print_header(msg: str):
    print(f"\n{'=' * 60}")
    print(msg)
    print('=' * 60)

def print_msg(msg: str):
    print(f"  {msg}")

def print_error(msg: str):
    print(f"❌ ERROR: {msg}")

def print_warning(msg: str):
    print(f"⚠️  WARNING: {msg}")

def print_success(msg: str):
    print(f"✓ {msg}")


def load_json_from_msz(msz_path: Path, json_filename: str) -> Optional[str]:
    """
    Load a JSON file from an .msz archive.
    
    :param msz_path: Path to the .msz file
    :param json_filename: Name of the JSON file to extract
    :return: JSON string or None if not found
    """
    try:
        with zipfile.ZipFile(msz_path, 'r') as zip_ref:
            if json_filename not in zip_ref.namelist():
                log.error(f"File {json_filename} not found in {msz_path}")
                log.message(f"Available JSON files:")
                for name in zip_ref.namelist():
                    if name.endswith('.json'):
                        log.message(f"  - {name}")
                return None
            
            with zip_ref.open(json_filename) as json_file:
                json_string = json_file.read().decode('utf-8')
                return json_string
    except Exception as ex:
        log.error(f"Error loading JSON from .msz: {ex}")
        return None


def parse_drum_json(json_string: str) -> Optional[Dict[str, Any]]:
    """
    Parse a JSON string using JDXiJsonSysexParser.
    
    :param json_string: JSON string to parse
    :return: Parsed dictionary or None
    """
    parser = JDXiJsonSysexParser(json_string)
    parsed_data = parser.parse()
    return parsed_data


def main():
    """Main function to load and parse drum JSON file."""
    if len(sys.argv) < 3:
        log.error("Usage: python3 parse_drum_json.py <msz_file> <json_filename>")
        log.message("Example: python3 parse_drum_json.py tests/ceremony_from_software.msz jdxi_tone_data_19703e00.json")
        log.message("\nOr list all drum files:")
        log.message("Example: python3 parse_drum_json.py tests/ceremony_from_software.msz --list")
        return 1
    
    msz_path = Path(sys.argv[1])
    json_filename = sys.argv[2]
    
    if not msz_path.exists():
        log.error(f"File not found: {msz_path}")
        return 1
    
    # List mode
    if json_filename == "--list":
        print_header(f"Listing drum files in {msz_path}")
        try:
            with zipfile.ZipFile(msz_path, 'r') as zip_ref:
                drum_files = [f for f in zip_ref.namelist() if f.endswith('.json') and '1970' in f]
                print_msg(f"Found {len(drum_files)} drum files:")
                for name in sorted(drum_files):
                    print_msg(f"  - {name}")
                
                # Check for common file
                common_files = [f for f in drum_files if '19700000' in f]
                if common_files:
                    print_success(f"Found Drum Common file(s):")
                    for f in common_files:
                        print_msg(f"  - {f}")
                else:
                    print_warning("Drum Common file (19700000) NOT FOUND")
        except Exception as ex:
            print_error(f"Error listing files: {ex}")
            return 1
        return 0
    
    print_header(f"Loading {json_filename} from {msz_path}")
    
    # Load JSON from .msz
    json_string = load_json_from_msz(msz_path, json_filename)
    if not json_string:
        return 1
    
    print_success(f"Loaded JSON file ({len(json_string)} bytes)")
    
    # Parse using JDXiJsonSysexParser
    print_header("Parsing JSON with JDXiJsonSysexParser...")
    parsed_data = parse_drum_json(json_string)
    
    if not parsed_data:
        print_error("Failed to parse JSON")
        return 1
    
    print_success("Parsed successfully!")
    print_header("Parsed Data Summary:")
    print_msg(f"ADDRESS: {parsed_data.get('ADDRESS', 'N/A')}")
    print_msg(f"TEMPORARY_AREA: {parsed_data.get('TEMPORARY_AREA', 'N/A')}")
    print_msg(f"SYNTH_TONE: {parsed_data.get('SYNTH_TONE', 'N/A')}")
    
    # Check if it's a common file
    if parsed_data.get('ADDRESS') == '19700000' or 'KIT_LEVEL' in parsed_data:
        print_header("Drum Common Parameters:")
        if 'KIT_LEVEL' in parsed_data:
            print_success(f"KIT_LEVEL: {parsed_data['KIT_LEVEL']}")
        else:
            print_warning("KIT_LEVEL: NOT FOUND")
    
    # Show key parameters for partial files
    if parsed_data.get('ADDRESS') != '19700000':
        print_header("Key Partial Parameters:")
        key_params = ['PARTIAL_LEVEL', 'PARTIAL_COARSE_TUNE', 'PARTIAL_FINE_TUNE', 'PARTIAL_PAN', 'MUTE_GROUP']
        for key in key_params:
            if key in parsed_data:
                print_msg(f"{key}: {parsed_data[key]}")
    
    # Count total parameters
    param_count = len([k for k in parsed_data.keys() if k not in ['JD_XI_HEADER', 'ADDRESS', 'TEMPORARY_AREA', 'SYNTH_TONE']])
    print_msg(f"\nTotal parameters: {param_count}")
    
    # Show all parameters (optional, can be verbose)
    if len(sys.argv) > 3 and sys.argv[3] == "--verbose":
        print_header("All Parameters:")
        for key, value in sorted(parsed_data.items()):
            if key not in ['JD_XI_HEADER', 'ADDRESS', 'TEMPORARY_AREA', 'SYNTH_TONE']:
                print_msg(f"{key}: {value}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

