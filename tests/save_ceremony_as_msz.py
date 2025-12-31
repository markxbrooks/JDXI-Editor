"""
Script to save the parsed Ceremony program (F18) JSON as a .msz file.

This script:
1. Loads the parsed JSON file from tests/jdxi_program_f18_parsed.json
2. Groups messages by address (synth section)
3. Creates JSON files for each synth section
4. Zips them into a .msz file
"""

import json
import zipfile
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Any

# Import logger only if available, otherwise use print
try:
    from jdxi_editor.log.logger import Logger as log
except ImportError:
    # Fallback logger using print
    class SimpleLogger:
        @staticmethod
        def message(msg: str) -> None:
            print(f"INFO: {msg}")
        
        @staticmethod
        def error(msg: str) -> None:
            print(f"ERROR: {msg}")
        
        @staticmethod
        def header_message(msg: str) -> None:
            print(f"\n{'=' * 60}")
            print(f"{msg}")
            print(f"{'=' * 60}")
    
    log = SimpleLogger()


def group_messages_by_address(messages: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Group messages by their ADDRESS field.
    
    :param messages: List of message dictionaries
    :return: Dictionary mapping addresses to message data
    """
    grouped: Dict[str, Dict[str, Any]] = {}
    
    for message in messages:
        address = message.get("ADDRESS", "")
        if not address:
            continue
        
        # If we've already seen this address, merge the parameters
        if address in grouped:
            # Merge parameters from this message into the existing one
            for key, value in message.items():
                if key not in ["ADDRESS", "JD_XI_HEADER", "TEMPORARY_AREA", "SYNTH_TONE"]:
                    grouped[address][key] = value
        else:
            # Create a new entry for this address
            grouped[address] = message.copy()
    
    # Add Digital Synth 2 Common if missing (we know TONE_LEVEL should be 107)
    if "12192100" not in grouped:
        log.message("Digital Synth 2 Common not found in parsed JSON, adding with TONE_LEVEL=107")
        grouped["12192100"] = {
            "JD_XI_HEADER": "f041100000000e",
            "ADDRESS": "12192100",  # Digital Synth 2 Common (19 21 00 00)
            "TEMPORARY_AREA": "DIGITAL_SYNTH_2",
            "SYNTH_TONE": "COMMON",
            "TONE_LEVEL": 107,  # From the SysEx message F0 41 10 00 00 00 0E 12 12 19 20 0C 6B 5E F7
            # Add minimal required parameters with default values
            "PORTAMENTO_SWITCH": 0,
            "PORTAMENTO_TIME": 0,
            "MONO_SWITCH": 0,
            "OCTAVE_SHIFT": 64,
            "PITCH_BEND_UP": 0,
            "PITCH_BEND_DOWN": 0,
        }
    
    return grouped


def save_msz_from_json(json_file_path: Path, output_msz_path: Path) -> bool:
    """
    Convert parsed JSON file to .msz format.
    
    :param json_file_path: Path to the parsed JSON file
    :param output_msz_path: Path where the .msz file should be saved
    :return: True if successful, False otherwise
    """
    try:
        # Load the parsed JSON file
        log.message(f"Loading JSON file: {json_file_path}")
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if "messages" not in data:
            log.error("JSON file does not contain 'messages' key")
            return False
        
        messages = data["messages"]
        log.message(f"Found {len(messages)} messages in JSON file")
        
        # Group messages by address
        grouped_messages = group_messages_by_address(messages)
        log.message(f"Grouped into {len(grouped_messages)} unique addresses")
        
        # Create a temporary directory for JSON files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create JSON files for each address
            json_files_created = []
            for address, message_data in grouped_messages.items():
                # Create filename based on address (same format as JDXiJSONComposer)
                json_filename = f"jdxi_tone_data_{address}.json"
                json_file_path = temp_path / json_filename
                
                # Save the message data as JSON
                with open(json_file_path, "w", encoding="utf-8") as f:
                    json.dump(message_data, f, indent=2)
                
                json_files_created.append(json_filename)
                temp_area = message_data.get("TEMPORARY_AREA", "UNKNOWN")
                synth_tone = message_data.get("SYNTH_TONE", "UNKNOWN")
                log.message(f"Created JSON file: {json_filename}")
                log.message(f"  Address: {address}, Area: {temp_area}, Tone: {synth_tone}")
            
            # Create the .msz file (ZIP archive)
            log.message(f"Creating .msz file: {output_msz_path}")
            with zipfile.ZipFile(output_msz_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for json_file in json_files_created:
                    file_path = temp_path / json_file
                    zipf.write(file_path, json_file)
                    log.message(f"Added {json_file} to .msz archive")
            
            log.header_message(f"Successfully created .msz file: {output_msz_path}")
            log.message(f"  - {len(json_files_created)} JSON files included")
            return True
            
    except Exception as ex:
        log.error(f"Error creating .msz file: {ex}")
        return False


def main():
    """Main function to save Ceremony program as .msz file."""
    import sys
    
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Paths
    script_dir = Path(__file__).parent
    json_file = script_dir / "jdxi_program_f18_parsed.json"
    output_msz = script_dir / "ceremony_f18.msz"
    
    # Check if JSON file exists
    if not json_file.exists():
        print(f"ERROR: JSON file not found: {json_file}")
        return 1
    
    # Save as .msz
    print("=" * 60)
    print("Converting Ceremony Program F18 JSON to .msz format")
    print("=" * 60)
    success = save_msz_from_json(json_file, output_msz)
    
    if success:
        print(f"\n✓ Successfully created: {output_msz}")
        if output_msz.exists():
            print(f"  File size: {output_msz.stat().st_size} bytes")
        return 0
    else:
        print("ERROR: Failed to create .msz file")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

