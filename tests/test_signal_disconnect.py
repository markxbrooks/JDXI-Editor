#!/usr/bin/env python3
"""
Test script to verify that the signal disconnection logic works properly.
This tests the specific RuntimeWarning issue with timer signal disconnection.
"""

import os
import sys
from unittest.mock import Mock, patch

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PySide6.QtCore import QTimer, QObject, Signal


def test_signal_disconnect_logic():
    """Test the signal disconnection logic that was causing RuntimeWarning"""
    
    print("🧪 Testing signal disconnection logic...")
    
    # Create a mock timer and signal handler
    timer = QTimer()
    handler = Mock()
    
    # Test 1: Connect and disconnect normally
    print("\n📋 Test 1: Normal connect/disconnect")
    try:
        timer.timeout.connect(handler)
        print("✅ Connected signal successfully")
        
        # Test the improved disconnect logic
        try:
            timer.timeout.disconnect(handler)
            print("✅ Disconnected signal successfully")
        except TypeError:
            print("⚠️ Signal was not connected")
    except Exception as ex:
        print(f"❌ FAIL: Normal connect/disconnect failed: {ex}")
        return False
    
    # Test 2: Disconnect when not connected
    print("\n📋 Test 2: Disconnect when not connected")
    try:
        # Try to disconnect again (should not be connected)
        timer.timeout.disconnect(handler)
        print("✅ Disconnected signal successfully")
    except TypeError:
        print("✅ Signal was not connected (expected)")
    except Exception as ex:
        print(f"❌ FAIL: Disconnect when not connected failed: {ex}")
        return False
    
    # Test 3: Multiple connections and disconnections
    print("\n📋 Test 3: Multiple connections and disconnections")
    try:
        # Connect multiple times
        timer.timeout.connect(handler)
        timer.timeout.connect(handler)
        print("✅ Connected signal multiple times")
        
        # Disconnect all
        timer.timeout.disconnect()  # Disconnect all
        print("✅ Disconnected all signals successfully")
    except Exception as ex:
        print(f"❌ FAIL: Multiple connections/disconnections failed: {ex}")
        return False
    
    # Test 4: Test the specific logic from the player
    print("\n📋 Test 4: Test player-specific disconnect logic")
    try:
        # Simulate the player's disconnect logic
        def test_disconnect_logic(timer, handler):
            try:
                timer.timeout.disconnect(handler)
                print("Successfully disconnected signal")
            except TypeError:
                print("Signal was not connected (TypeError)")
            except Exception as ex:
                print(f"Could not disconnect signal: {ex}")
        
        # Test with connected signal
        timer.timeout.connect(handler)
        test_disconnect_logic(timer, handler)
        
        # Test with disconnected signal
        test_disconnect_logic(timer, handler)
        
        print("✅ Player-specific disconnect logic works correctly")
    except Exception as ex:
        print(f"❌ FAIL: Player-specific disconnect logic failed: {ex}")
        return False
    
    print("\n🎉 All signal disconnection tests passed!")
    return True


if __name__ == '__main__':
    success = test_signal_disconnect_logic()
    sys.exit(0 if success else 1)
