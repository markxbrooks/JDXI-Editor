#!/usr/bin/env python3
"""
SINCO VMX8 Controller Test using MidiIOHelper

This test uses the existing MidiIOHelper from the JD-Xi Editor codebase,
which should handle MIDI callbacks properly.
"""

import sys
import time
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

# Add the project root to the path
sys.path.insert(0, '/Users/brooks/projects/JDXI-Editor')

# Import compatibility module first
import rtmidi_compat

from jdxi_editor.midi.io.helper import MidiIOHelper
from decologr import setup_logging

class ControllerTestApp:
    def __init__(self):
        self.app = QCoreApplication(sys.argv)
        self.midi_helper = MidiIOHelper()
        self.setup_connections()
        self.message_count = 0
        
    def setup_connections(self):
        """Connect MIDI signals to test handlers"""
        self.midi_helper.midi_control_changed.connect(self.on_control_change)
        self.midi_helper.midi_program_changed.connect(self.on_program_change)
        self.midi_helper.midi_message_incoming.connect(self.on_midi_message)
        self.midi_helper.midi_sysex_json.connect(self.on_sysex_json)
        
    def on_control_change(self, channel, control, value):
        """Handle control change messages"""
        self.message_count += 1
        print(f"🎛️  Control Change #{self.message_count}: Channel {channel}, CC{control}, Value {value}")
        
        # Highlight the specific messages from your controller
        if control == 10:  # Pan (fine)
            print(f"   → PAN FINE detected! Value: {value}")
        elif control == 41:  # Controller 41
            print(f"   → CC41 detected! Value: {value}")
        
    def on_program_change(self, channel, program):
        """Handle program change messages"""
        self.message_count += 1
        print(f"🎵 Program Change #{self.message_count}: Channel {channel}, Program {program}")
        
    def on_midi_message(self, message):
        """Handle any MIDI message"""
        self.message_count += 1
        print(f"📡 MIDI Message #{self.message_count}: {message.type} - {message}")
        
    def on_sysex_json(self, json_data):
        """Handle SysEx JSON data"""
        self.message_count += 1
        print(f"🔧 SysEx JSON #{self.message_count}: {json_data}")
        
    def test_controller(self):
        """Test SINCO VMX8 controller using MidiIOHelper"""
        print("=== SINCO VMX8 Controller Test using MidiIOHelper ===")
        
        # List available ports
        input_ports = self.midi_helper.get_input_ports()
        print(f"Available input ports: {input_ports}")
        
        # Find SINCO ports
        sinco_ports = []
        for i, port in enumerate(input_ports):
            if "SINCO" in port.upper() or "VMX8" in port.upper():
                sinco_ports.append((i, port))
        
        if not sinco_ports:
            print("❌ No SINCO VMX8 ports found")
            return False
            
        print(f"Found SINCO VMX8 ports: {[port[1] for port in sinco_ports]}")
        
        # Test each SINCO port
        for port_index, port_name in sinco_ports:
            print(f"\n=== Testing Port: {port_name} ===")
            
            if self.midi_helper.open_input_port(port_name):
                print(f"✅ Successfully connected to {port_name}")
                print("Move controls on your SINCO VMX8 controller...")
                print("Monitoring for 15 seconds...\n")
                
                # Monitor for 15 seconds
                start_time = time.time()
                while time.time() - start_time < 15:
                    self.app.processEvents()
                    time.sleep(0.01)
                
                if self.message_count > 0:
                    print(f"\n✅ SUCCESS! Received {self.message_count} messages from {port_name}")
                else:
                    print(f"\n❌ No messages received from {port_name}")
                
                # Close the port
                self.midi_helper.close_ports()
                print(f"✅ Closed {port_name}")
                
                # Reset message count for next port
                self.message_count = 0
                
            else:
                print(f"❌ Failed to connect to {port_name}")
        
        return True

def main():
    print("SINCO VMX8 Controller Test using MidiIOHelper")
    print("=" * 60)
    
    # Set up logging
    logger = setup_logging(log_level=20)  # INFO level
    
    # Create test app
    test_app = ControllerTestApp()
    
    # Run test
    success = test_app.test_controller()
    
    if success:
        print("\n✅ Controller test completed!")
        print("The MidiIOHelper should properly handle MIDI callbacks.")
    else:
        print("\n❌ Controller test failed!")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
