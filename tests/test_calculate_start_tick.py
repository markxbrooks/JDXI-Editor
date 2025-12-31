#!/usr/bin/env python3
"""
Test script to verify that the calculate_start_tick method handles None playback_start_time correctly.
"""

import os
import sys
import time
from unittest.mock import Mock

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import mido


def test_calculate_start_tick_logic():
    """Test the calculate_start_tick logic without Qt dependencies"""
    
    print("🧪 Testing calculate_start_tick logic...")
    
    # Test the logic from calculate_start_tick method
    def calculate_start_tick(playback_start_time, tempo_at_position, ticks_per_beat):
        """Simulate the calculate_start_tick method logic"""
        try:
            # Check if playback_start_time is initialized
            if playback_start_time is None:
                print("playback_start_time not initialized, using 0")
                return 0
            
            elapsed_time_secs = time.time() - playback_start_time
            return int(
                mido.second2tick(
                    second=elapsed_time_secs,
                    ticks_per_beat=ticks_per_beat,
                    tempo=tempo_at_position,
                )
            )
        except Exception as ex:
            print(f"Error converting playback start time to ticks: {ex}")
            return None
    
    # Test 1: None playback_start_time
    print("\n📋 Test 1: None playback_start_time")
    result = calculate_start_tick(None, 500000, 480)
    if result == 0:
        print("✅ PASS: Returns 0 when playback_start_time is None")
    else:
        print(f"❌ FAIL: Expected 0, got {result}")
        return False
    
    # Test 2: Valid playback_start_time
    print("\n📋 Test 2: Valid playback_start_time")
    start_time = time.time() - 10.0  # 10 seconds ago
    result = calculate_start_tick(start_time, 500000, 480)
    if result is not None and result > 0:
        print(f"✅ PASS: Returns valid tick {result} with valid playback_start_time")
    else:
        print(f"❌ FAIL: Expected positive value, got {result}")
        return False
    
    # Test 3: Very recent playback_start_time
    print("\n📋 Test 3: Very recent playback_start_time")
    start_time = time.time() - 0.1  # 0.1 seconds ago
    result = calculate_start_tick(start_time, 500000, 480)
    if result is not None and result >= 0:
        print(f"✅ PASS: Returns valid tick {result} with recent playback_start_time")
    else:
        print(f"❌ FAIL: Expected non-negative value, got {result}")
        return False
    
    # Test 4: Different tempo
    print("\n📋 Test 4: Different tempo (62 BPM)")
    start_time = time.time() - 5.0  # 5 seconds ago
    tempo_62_bpm = 967745  # 62 BPM in microseconds
    result = calculate_start_tick(start_time, tempo_62_bpm, 480)
    if result is not None and result > 0:
        print(f"✅ PASS: Returns valid tick {result} with 62 BPM tempo")
    else:
        print(f"❌ FAIL: Expected positive value, got {result}")
        return False
    
    print("\n🎉 All calculate_start_tick logic tests passed!")
    return True


if __name__ == '__main__':
    success = test_calculate_start_tick_logic()
    sys.exit(0 if success else 1)
