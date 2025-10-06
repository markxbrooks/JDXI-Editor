#!/usr/bin/env python3
"""
SINCO VMX8 Controller Integration Test

This script tests the integration of your SINCO VMX8 controller with the JD-Xi Editor.
It uses the same MIDI handling code as the main application.
"""

import sys
import time
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

# Add the project root to the path
sys.path.insert(0, '/Users/brooks/projects/JDXI-Editor')

# Import compatibility module first
import rtmidi_compat

from jdxi_editor.midi.io.input_handler import MidiInHandler
from jdxi_editor.log.setup import setup_logging

class ControllerTestApp:
    def __init__(self):
        self.app = QCoreApplication(sys.argv)
        self.midi_handler = MidiInHandler()
        self.setup_connections()
        
    def setup_connections(self):
        """Connect MIDI signals to test handlers"""
        self.midi_handler.midi_control_changed.connect(self.on_control_change)
        self.midi_handler.midi_program_changed.connect(self.on_program_change)
        self.midi_handler.midi_message_incoming.connect(self.on_midi_message)
        
    def on_control_change(self, channel, control, value):
        """Handle control change messages"""
        print(f"🎛️  Control Change: Channel {channel}, CC{control}, Value {value}")
        
        # Test specific CC41 messages from your controller
        if control == 41:
            print(f"   → SINCO VMX8 Controller 41 detected! Value: {value}")
            if value in [4, 6, 7, 9]:
                print(f"   → This matches your recorded values!")
        
    def on_program_change(self, channel, program):
        """Handle program change messages"""
        print(f"🎵 Program Change: Channel {channel}, Program {program}")
        
    def on_midi_message(self, message):
        """Handle any MIDI message"""
        print(f"📡 MIDI Message: {message.type} - {message}")
        
    def test_connection(self):
        """Test MIDI connection"""
        print("=== SINCO VMX8 Controller Integration Test ===")
        
        # List available ports
        input_ports = self.midi_handler.get_input_ports()
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
        
        # Connect to the first SINCO port
        port_index, port_name = sinco_ports[0]
        print(f"Connecting to: {port_name}")
        
        if self.midi_handler.open_input_port(port_name):
            print("✅ Successfully connected to SINCO VMX8 controller")
            print("\n=== Monitoring Controller Input ===")
            print("Move controls on your SINCO VMX8 controller...")
            print("Press Ctrl+C to stop monitoring\n")
            
            try:
                # Monitor for 30 seconds
                start_time = time.time()
                while time.time() - start_time < 30:
                    self.app.processEvents()
                    time.sleep(0.01)
                    
            except KeyboardInterrupt:
                print("\n=== Test Interrupted ===")
                
            finally:
                self.midi_handler.close_ports()
                print("✅ MIDI connection closed")
                
            return True
        else:
            print("❌ Failed to connect to SINCO VMX8 controller")
            return False

def main():
    print("SINCO VMX8 Controller Integration Test")
    print("=" * 50)
    
    # Set up logging
    logger = setup_logging(log_level=20)  # INFO level
    
    # Create test app
    test_app = ControllerTestApp()
    
    # Run test
    success = test_app.test_connection()
    
    if success:
        print("\n✅ Controller integration test completed successfully!")
        print("Your SINCO VMX8 controller is working with the JD-Xi Editor!")
    else:
        print("\n❌ Controller integration test failed!")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
