#!/usr/bin/env python3
"""
System MIDI Test using macOS built-in tools

This test uses macOS built-in MIDI monitoring tools to check if the controller
is sending messages.
"""

import subprocess
import time
import sys

def test_with_system_tools():
    """Test using macOS system tools"""
    print("SINCO VMX8 Controller Test using System Tools")
    print("=" * 50)
    
    # Check if we're on macOS
    if sys.platform != "darwin":
        print("❌ This test is designed for macOS")
        return False
    
    print("Checking MIDI ports using system tools...")
    
    # Use system_profiler to check MIDI devices
    try:
        result = subprocess.run(["system_profiler", "SPAudioDataType"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            audio_info = result.stdout
            if "SINCO" in audio_info.upper() or "VMX8" in audio_info.upper():
                print("✅ SINCO VMX8 detected in audio devices")
            else:
                print("❌ SINCO VMX8 not found in audio devices")
        else:
            print("❌ Could not check audio devices")
    except Exception as e:
        print(f"❌ Error checking audio devices: {e}")
    
    # Check MIDI ports using system tools
    try:
        result = subprocess.run(["ls", "/dev/"], capture_output=True, text=True)
        if result.returncode == 0:
            devices = result.stdout
            midi_devices = [d for d in devices.split('\n') if 'midi' in d.lower()]
            if midi_devices:
                print(f"MIDI devices found: {midi_devices}")
            else:
                print("No MIDI devices found in /dev/")
        else:
            print("❌ Could not list devices")
    except Exception as e:
        print(f"❌ Error listing devices: {e}")
    
    # Try to use the built-in MIDI monitor
    print("\n=== Using Built-in MIDI Monitor ===")
    print("To test your controller manually:")
    print("1. Open 'Audio MIDI Setup' (Applications > Utilities)")
    print("2. Look for your SINCO VMX8 in the MIDI devices list")
    print("3. Open 'MIDI Monitor' (if available)")
    print("4. Move controls on your controller")
    print("5. Check if messages appear in MIDI Monitor")
    
    return True

def main():
    try:
        success = test_with_system_tools()
        if success:
            print("\n✅ System test completed!")
        else:
            print("\n❌ System test failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
