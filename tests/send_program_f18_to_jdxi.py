#!/usr/bin/env python3
"""
Script to load the parsed Program F18 JSON file and send it back to the JD-Xi as SysEx messages.

This script:
1. Loads the JSON file from the tests directory
2. Parses each message using JDXiJsonSysexParser
3. Sends each message to the JD-Xi as SysEx
"""

import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtCore import QCoreApplication
from jdxi_editor.midi.io.helper import MidiIOHelper
from decologr import Decologr as log


def load_json_file(file_path: Path) -> Dict[str, Any] | None:
    """
    Load JSON file containing parsed SysEx messages.
    
    :param file_path: Path to JSON file
    :return: dict Parsed JSON data or None if loading fails
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as ex:
        log.error(f"Failed to load JSON file: {ex}")
        return None


def send_messages_to_jdxi(midi_helper: MidiIOHelper, messages: List[Dict[str, Any]]) -> None:
    """
    Send multiple JSON SysEx messages to the JD-Xi.
    
    :param midi_helper: MidiIOHelper instance
    :param messages: List of message dictionaries
    """
    total_messages = len(messages)
    log.header_message(f"Sending {total_messages} SysEx messages to JD-Xi...")
    
    sent_count = 0
    failed_count = 0
    
    for i, message in enumerate(messages, 1):
        address = message.get(SysExSection.ADDRESS, "unknown")
        temporary_area = message.get(SysExSection.TEMPORARY_AREA, "unknown")
        synth_tone = message.get(SysExSection.SYNTH_TONE, "unknown")
        
        log.message(f"[{i}/{total_messages}] Sending message - ADDRESS: {address}, AREA: {temporary_area}, TONE: {synth_tone}")
        
        # Convert message dict to JSON string
        try:
            json_string = json.dumps(message)
            
            # Send to JD-Xi
            midi_helper.send_json_patch_to_instrument(json_string)
            sent_count += 1
            
            # Small delay between messages to avoid overwhelming the device
            time.sleep(0.05)  # 50ms delay
            
        except Exception as ex:
            log.error(f"Failed to send message {i}: {ex}")
            failed_count += 1
    
    log.header_message(f"✓ Completed sending messages")
    log.message(f"Successfully sent: {sent_count}/{total_messages}")
    if failed_count > 0:
        log.warning(f"Failed to send: {failed_count}/{total_messages}")


def main():
    """Main function."""
    # Create Qt application
    app = QCoreApplication(sys.argv)
    
    # Determine JSON file path
    json_file = Path(__file__).parent / "jdxi_program_f18_parsed.json"
    
    if not json_file.exists():
        log.error(f"JSON file not found: {json_file}")
        log.message("Please ensure the file exists in the tests directory")
        return 1
    
    log.message(f"Loading JSON file: {json_file}")
    
    # Load JSON file
    data = load_json_file(json_file)
    if not data:
        return 1
    
    # Extract messages
    messages = data.get("messages", [])
    if not messages:
        log.error("No messages found in JSON file")
        return 1
    
    program_info = f"{data.get('bank', '?')}{data.get('program_number', '?')}"
    log.header_message(f"Loaded Program {program_info} with {len(messages)} messages")
    
    # Initialize MIDI helper
    log.message("Initializing MIDI helper...")
    midi_helper = MidiIOHelper()
    
    # Auto-connect to JD-Xi
    log.message("Attempting to auto-connect to JD-Xi...")
    if not midi_helper.auto_connect_jdxi():
        log.error("Could not find or connect to JD-Xi MIDI ports. Please ensure the device is connected.")
        return 1
    
    log.message(f"Connected to JD-Xi ports - Input: {midi_helper.in_port_name}, Output: {midi_helper.out_port_name}")
    
    # Send messages
    send_messages_to_jdxi(midi_helper, messages)
    
    # Small delay before exiting
    time.sleep(0.5)
    
    log.header_message("Done!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

