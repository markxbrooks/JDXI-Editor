#!/usr/bin/env python3
"""
SINCO VMX8 Controller Diagnostics

This script provides comprehensive diagnostics for your SINCO VMX8 controller
to help identify why MIDI messages aren't being received.
"""

import os
import subprocess
import sys
import time
from typing import List, Optional

import rtmidi


class ControllerDiagnostics:
    def __init__(self):
        self.ports = []
        
    def run_diagnostics(self):
        """Run comprehensive diagnostics"""
        print("SINCO VMX8 Controller Diagnostics")
        print("=" * 50)
        
        # 1. Check system MIDI ports
        self.check_midi_ports()
        
        # 2. Check USB devices
        self.check_usb_devices()
        
        # 3. Check system logs
        self.check_system_logs()
        
        # 4. Test MIDI library
        self.test_midi_library()
        
        # 5. Provide recommendations
        self.provide_recommendations()
    
    def check_midi_ports(self):
        """Check available MIDI ports"""
        print("\n1. MIDI Port Analysis")
        print("-" * 30)
        
        try:
            midi_in = rtmidi.RtMidiIn()
            port_count = midi_in.getPortCount()
            
            print(f"Total MIDI input ports: {port_count}")
            
            for i in range(port_count):
                port_name = midi_in.getPortName(i)
                self.ports.append(port_name)
                print(f"  {i}: {port_name}")
                
                # Check if it's a SINCO port
                if "SINCO" in port_name.upper() or "VMX8" in port_name.upper():
                    print(f"    → SINCO VMX8 port detected!")
                    
        except Exception as e:
            print(f"❌ Error checking MIDI ports: {e}")
    
    def check_usb_devices(self):
        """Check USB devices for SINCO controller"""
        print("\n2. USB Device Analysis")
        print("-" * 30)
        
        try:
            # Check for USB devices on macOS
            if sys.platform == "darwin":
                result = subprocess.run(["system_profiler", "SPUSBDataType"], 
                                      capture_output=True, text=True)
                usb_info = result.stdout
                
                if "SINCO" in usb_info.upper() or "VMX8" in usb_info.upper():
                    print("✅ SINCO VMX8 detected in USB devices")
                    # Extract relevant lines
                    lines = usb_info.split('\n')
                    in_sinco_section = False
                    for line in lines:
                        if "SINCO" in line.upper() or "VMX8" in line.upper():
                            in_sinco_section = True
                        if in_sinco_section:
                            print(f"    {line.strip()}")
                            if line.strip() == "":
                                break
                else:
                    print("❌ SINCO VMX8 not found in USB devices")
                    print("   This might indicate a driver or connection issue")
                    
        except Exception as e:
            print(f"❌ Error checking USB devices: {e}")
    
    def check_system_logs(self):
        """Check system logs for MIDI-related messages"""
        print("\n3. System Log Analysis")
        print("-" * 30)
        
        try:
            if sys.platform == "darwin":
                # Check for MIDI-related log entries
                result = subprocess.run(["log", "show", "--last", "1h", "--predicate", 
                                       "category == 'MIDI' OR category == 'Audio'"], 
                                      capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and result.stdout:
                    print("✅ Found MIDI-related log entries")
                    # Show last few lines
                    lines = result.stdout.split('\n')[-10:]
                    for line in lines:
                        if line.strip():
                            print(f"    {line.strip()}")
                else:
                    print("ℹ️  No recent MIDI log entries found")
                    
        except Exception as e:
            print(f"ℹ️  Could not check system logs: {e}")
    
    def test_midi_library(self):
        """Test MIDI library functionality"""
        print("\n4. MIDI Library Test")
        print("-" * 30)
        
        try:
            # Test basic MIDI functionality
            midi_in = rtmidi.RtMidiIn()
            midi_out = rtmidi.RtMidiOut()
            
            print("✅ MIDI library loaded successfully")
            print(f"   Input ports: {midi_in.getPortCount()}")
            print(f"   Output ports: {midi_out.getPortCount()}")
            
            # Test port opening
            if self.ports:
                for i, port_name in enumerate(self.ports):
                    try:
                        midi_in.openPort(i)
                        print(f"✅ Successfully opened port {i}: {port_name}")
                        midi_in.closePort()
                    except Exception as e:
                        print(f"❌ Failed to open port {i} ({port_name}): {e}")
                        
        except Exception as e:
            print(f"❌ MIDI library test failed: {e}")
    
    def provide_recommendations(self):
        """Provide troubleshooting recommendations"""
        print("\n5. Troubleshooting Recommendations")
        print("-" * 40)
        
        sinco_ports = [p for p in self.ports if "SINCO" in p.upper() or "VMX8" in p.upper()]
        
        if sinco_ports:
            print("✅ SINCO VMX8 ports are detected by the system")
            print("\nPossible issues:")
            print("1. Controller Mode:")
            print("   - Check if the controller has a MIDI mode setting")
            print("   - Look for a 'MIDI' button or mode selector")
            print("   - Some controllers need to be in MIDI mode to send data")
            
            print("\n2. Controller Settings:")
            print("   - Check if there's a MIDI channel setting")
            print("   - Look for a 'MIDI Enable' or similar setting")
            print("   - Some controllers have a 'Local Off' mode")
            
            print("\n3. Physical Controls:")
            print("   - Try different faders, knobs, and buttons")
            print("   - Some controls might not send MIDI by default")
            print("   - Check if there's a 'MIDI Learn' mode")
            
            print("\n4. Software Settings:")
            print("   - The controller might be sending to a different application")
            print("   - Check if Logic Pro or another DAW is capturing the MIDI")
            print("   - Try closing other MIDI applications")
            
        else:
            print("❌ SINCO VMX8 ports not detected")
            print("\nPossible issues:")
            print("1. Driver Issues:")
            print("   - The controller might need specific drivers")
            print("   - Check the manufacturer's website for drivers")
            print("   - Try installing the latest drivers")
            
            print("\n2. Connection Issues:")
            print("   - Try a different USB cable")
            print("   - Try a different USB port")
            print("   - Check if the controller is powered on")
            
            print("\n3. Controller Issues:")
            print("   - The controller might be in a different mode")
            print("   - Check if there's a power switch or mode selector")
            print("   - Try resetting the controller")
        
        print("\n6. Next Steps")
        print("-" * 15)
        print("1. Check the controller's manual for MIDI settings")
        print("2. Look for a 'MIDI' mode or button on the controller")
        print("3. Try different controls (faders, knobs, buttons)")
        print("4. Check if the controller has a MIDI channel setting")
        print("5. Try connecting to a different computer to test")
        print("6. Contact SINCO support if the issue persists")

def main():
    diagnostics = ControllerDiagnostics()
    diagnostics.run_diagnostics()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
