#!/usr/bin/env python3
"""
Replicate Working App Approach

This attempts to replicate the approach used by the working MIDI monitoring app
that successfully captured your controller's messages.
"""

import sys
import time
import rtmidi
from PySide6.QtCore import QCoreApplication, QTimer
from PySide6.QtWidgets import QApplication

# Add the project root to the path
sys.path.insert(0, '/Users/brooks/projects/JDXI-Editor')

# Import compatibility module first
import rtmidi_compat

class WorkingAppReplicator:
    def __init__(self):
        self.app = QCoreApplication(sys.argv)
        self.midi_in = None
        self.message_count = 0
        self.start_time = None
        
    def midi_callback(self, message, data):
        """Callback that should work like the successful app"""
        message_data, timestamp = message
        self.message_count += 1
        
        # Format timestamp like your working app
        elapsed = time.time() - self.start_time if self.start_time else 0
        timestamp_str = f"{elapsed:.3f}"
        
        # Decode the message
        if len(message_data) >= 3:
            status = message_data[0]
            if status == 0xB0:  # Control Change
                channel = (status & 0x0F) + 1
                controller = message_data[1]
                value = message_data[2]
                
                # Format like your working app
                if controller == 10:
                    print(f"{timestamp_str:>8}\tFrom SINCO VMX8-Private\tControl\t{channel}\tPan (fine)\t{value}")
                elif controller == 41:
                    print(f"{timestamp_str:>8}\tFrom SINCO VMX8-Private\tControl\t{channel}\tController 41\t{value}")
                else:
                    print(f"{timestamp_str:>8}\tFrom SINCO VMX8-Private\tControl\t{channel}\tController {controller}\t{value}")
            else:
                print(f"{timestamp_str:>8}\tFrom SINCO VMX8-Private\tOther\t{message_data}")
        else:
            print(f"{timestamp_str:>8}\tFrom SINCO VMX8-Private\tRaw\t{message_data}")
    
    def test_ports(self):
        """Test both SINCO ports"""
        print("=== Replicating Working App Approach ===")
        
        # Create MIDI input
        self.midi_in = rtmidi.RtMidiIn()
        
        # List ports
        port_count = self.midi_in.getPortCount()
        print(f"Available ports: {port_count}")
        
        ports = []
        for i in range(port_count):
            port_name = self.midi_in.getPortName(i)
            ports.append((i, port_name))
            print(f"  {i}: {port_name}")
        
        # Find SINCO ports
        sinco_ports = [(i, name) for i, name in ports if "SINCO" in name.upper() or "VMX8" in name.upper()]
        
        if not sinco_ports:
            print("❌ No SINCO ports found")
            return False
        
        print(f"\nFound SINCO ports: {sinco_ports}")
        
        # Test each port
        for port_index, port_name in sinco_ports:
            print(f"\n=== Testing {port_name} ===")
            
            try:
                # Close any existing port
                if self.midi_in.isPortOpen():
                    self.midi_in.closePort()
                
                # Open the port
                self.midi_in.openPort(port_index)
                print(f"✅ Opened {port_name}")
                
                # Set callback
                self.midi_in.setCallback(self.midi_callback)
                print("✅ Callback set")
                
                # Set ignore types
                self.midi_in.ignoreTypes(False, True, True)
                print("✅ Ignore types set")
                
                # Start monitoring
                self.start_time = time.time()
                self.message_count = 0
                
                print("Move controls on your SINCO VMX8 controller...")
                print("Monitoring for 15 seconds...\n")
                
                # Monitor with Qt event processing
                start_time = time.time()
                while time.time() - start_time < 15:
                    self.app.processEvents()
                    time.sleep(0.001)  # Very short sleep
                
                if self.message_count > 0:
                    print(f"\n✅ SUCCESS! Received {self.message_count} messages from {port_name}")
                else:
                    print(f"\n❌ No messages received from {port_name}")
                
                # Close port
                self.midi_in.closePort()
                print(f"✅ Closed {port_name}")
                
            except Exception as e:
                print(f"❌ Error testing {port_name}: {e}")
                try:
                    self.midi_in.closePort()
                except:
                    pass
        
        return True

def main():
    print("Replicating Working MIDI App Approach")
    print("=" * 50)
    
    replicator = WorkingAppReplicator()
    success = replicator.test_ports()
    
    if success:
        print("\n✅ Test completed!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
