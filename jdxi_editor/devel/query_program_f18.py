#!/usr/bin/env python3
"""
Script to query JD-Xi for Program Bank F, Program 18 and collect SysEx responses.

This script:
1. Connects to the JD-Xi MIDI ports
2. Loads Program Bank F, Program 18
3. Requests all parameter data
4. Captures all SysEx JSON responses
5. Saves them to a JSON file
"""

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

from PySide6.QtCore import QCoreApplication, QObject, QTimer, Signal

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from decologr import Decologr as log

from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.program.helper import JDXiProgramHelper
from jdxi_editor.midi.sysex.request.midi_requests import MidiRequests
from jdxi_editor.ui.editors.helpers.program import calculate_midi_values


class SysExCollector(QObject):
    """Collects SysEx JSON responses from the JD-Xi."""
    
    collection_complete = Signal()
    
    def __init__(self, output_file: Path):
        super().__init__()
        self.output_file = output_file
        self.collected_responses: List[Dict[str, Any]] = []
        self.collection_timeout = 10.0  # seconds
        self.start_time: float = 0.0
        
    def on_sysex_json(self, json_string: str) -> None:
        """
        Handle incoming SysEx JSON data.
        
        :param json_string: str JSON string containing SysEx data
        """
        try:
            data = json.loads(json_string)
            self.collected_responses.append(data)
            address = data.get(SysExSection.ADDRESS, "unknown")
            temporary_area = data.get(SysExSection.TEMPORARY_AREA, "unknown")
            synth_tone = data.get(SysExSection.SYNTH_TONE, "unknown")
            log.message(f"✓ Collected SysEx response #{len(self.collected_responses)} - ADDRESS: {address}, AREA: {temporary_area}, TONE: {synth_tone}")
        except json.JSONDecodeError as ex:
            log.error(f"Failed to parse JSON SysEx: {ex}")
    
    def start_collection(self) -> None:
        """Start the collection timer."""
        self.start_time = time.time()
        log.message(f"Started collecting SysEx responses (timeout: {self.collection_timeout}s)")
    
    def check_timeout(self) -> None:
        """Check if collection timeout has been reached."""
        elapsed = time.time() - self.start_time
        if elapsed >= self.collection_timeout:
            log.header_message(f"Collection timeout reached ({self.collection_timeout}s)")
            log.message(f"Total SysEx responses collected: {len(self.collected_responses)}")
            if len(self.collected_responses) == 0:
                log.warning("No SysEx responses were collected. The JD-Xi may not have responded, or the program may not exist.")
            self.save_responses()
            self.collection_complete.emit()
    
    def save_responses(self) -> None:
        """Save collected responses to JSON file."""
        try:
            output_data = {
                "program": "F18",
                "bank": "F",
                "program_number": 18,
                "total_responses": len(self.collected_responses),
                "responses": self.collected_responses
            }
            
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            log.header_message(f"✓ Successfully saved {len(self.collected_responses)} SysEx responses")
            log.message(f"Output file: {self.output_file}")
            
            # Log summary of collected responses
            if len(self.collected_responses) > 0:
                addresses = [r.get(SysExSection.ADDRESS, "unknown") for r in self.collected_responses]
                log.message(f"Collected addresses: {', '.join(set(addresses))}")
        except Exception as ex:
            log.error(f"Failed to save responses: {ex}")


def main():
    """Main function to query and collect program data."""
    # Create Qt application
    app = QCoreApplication(sys.argv)
    
    # Determine output file
    output_file = Path.home() / "jdxi_program_f18_sysex.json"
    log.message(f"Output file: {output_file}")
    
    # Initialize MIDI helper
    log.message("Initializing MIDI helper...")
    midi_helper = MidiIOHelper()
    
    # Find and open JD-Xi ports automatically
    log.message("Attempting to auto-connect to JD-Xi...")
    if not midi_helper.auto_connect_jdxi():
        log.error("Could not find or connect to JD-Xi MIDI ports. Please ensure the device is connected.")
        return 1
    
    log.message(f"Connected to JD-Xi ports - Input: {midi_helper.in_port_name}, Output: {midi_helper.out_port_name}")
    
    # Create SysEx collector
    collector = SysExCollector(output_file)
    midi_helper.midi_sysex_json.connect(collector.on_sysex_json)
    
    # Calculate MIDI values for Bank F, Program 18
    bank = "F"
    program_number = 18
    msb, lsb, pc = calculate_midi_values(bank, program_number)
    log.message(f"Bank {bank}, Program {program_number}: MSB={msb}, LSB={lsb}, PC={pc}")
    
    # Create program helper
    program_helper = JDXiProgramHelper(midi_helper, channel=1)
    
    # Set up collection timeout timer
    timeout_timer = QTimer()
    timeout_timer.timeout.connect(collector.check_timeout)
    timeout_timer.setSingleShot(False)
    timeout_timer.start(1000)  # Check every second
    
    # Start collection
    collector.start_collection()
    
    # Load the program
    log.header_message(f"Loading Program {bank}{program_number:02d}...")
    program_helper.load_program(bank, program_number)
    
    # Wait a moment for the program to load
    time.sleep(0.5)
    
    # Request data - this will trigger SysEx responses
    log.message("Requesting parameter data from JD-Xi...")
    program_helper.data_request()
    
    # Wait for collection to complete
    def on_collection_complete():
        log.header_message("Collection complete!")
        app.quit()
    
    collector.collection_complete.connect(on_collection_complete)
    
    # Set a maximum wait time
    max_wait_timer = QTimer()
    max_wait_timer.setSingleShot(True)
    max_wait_timer.timeout.connect(lambda: (
        collector.save_responses(),
        log.header_message("Maximum wait time reached. Saving and exiting..."),
        app.quit()
    ))
    max_wait_timer.start(int((collector.collection_timeout + 2) * 1000))
    
    # Run the application
    log.header_message("Waiting for SysEx responses from JD-Xi...")
    log.message("Note: Some parsing errors are normal for non-SysEx MIDI messages")
    log.message(f"Collection will timeout after {collector.collection_timeout} seconds")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

