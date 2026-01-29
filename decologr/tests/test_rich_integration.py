#!/usr/bin/env python3
"""
Test script to verify Rich integration and backward compatibility.
"""

import logging
import logging
from decologr import Decologr, setup_logging, set_project_name, log_exception

def test_basic_logging():
    """Test basic logging without Rich."""
    print("\n=== Test 1: Basic Logging (without Rich) ===")
    set_project_name("test_project")
    logger = setup_logging(use_rich=False, project_name="test_project")
    
    Decologr.debug("Debug message")
    Decologr.info("Info message")
    Decologr.warning("Warning message")
    Decologr.error("Error message")
    Decologr.critical("Critical message")
    
    print("✓ Basic logging works without Rich")

def test_rich_logging():
    """Test Rich-enhanced logging if Rich is available."""
    print("\n=== Test 2: Rich-Enhanced Logging ===")
    try:
        logger = setup_logging(use_rich=True, project_name="test_project")
        
        Decologr.debug("Debug message with Rich")
        Decologr.info("Info message with Rich")
        Decologr.warning("Warning message with Rich")
        Decologr.error("Error message with Rich")
        Decologr.critical("Critical message with Rich")
        
        print("✓ Rich logging works")
    except ImportError as e:
        print(f"⚠ Rich not available: {e}")
        print("  Install with: pip install decologr[rich]")

def test_auto_detect_rich():
    """Test auto-detection of Rich."""
    print("\n=== Test 3: Auto-detect Rich ===")
    try:
        # This should use Rich if available, otherwise fallback
        logger = setup_logging(use_rich=None, project_name="test_project")
        
        Decologr.info("Auto-detected Rich formatting")
        print("✓ Auto-detection works")
    except Exception as e:
        print(f"⚠ Error: {e}")

def test_json_logging():
    """Test JSON logging."""
    print("\n=== Test 4: JSON Logging ===")
    data = {"user": "alice", "action": "login", "timestamp": "2024-01-01"}
    Decologr.json(data)
    print("✓ JSON logging works")

def test_json_pretty_printing():
    """Test Rich JSON pretty-printing."""
    print("\n=== Test 4b: Rich JSON Pretty-Printing ===")
    try:
        complex_data = {
            "user": {
                "id": 12345,
                "name": "Alice",
                "email": "alice@example.com",
                "preferences": {
                    "theme": "dark",
                    "notifications": True,
                    "language": "en"
                }
            },
            "actions": ["login", "view", "edit"],
            "metadata": {
                "timestamp": "2024-01-01T12:00:00Z",
                "version": "1.0.0"
            }
        }
        
        print("Testing with pretty=True:")
        Decologr.json(complex_data, pretty=True)
        
        print("\nTesting with pretty=False (compact):")
        Decologr.json(complex_data, pretty=False)
        
        print("\nTesting with pretty=None (auto-detect):")
        Decologr.json(complex_data, pretty=None)
        
        print("✓ Rich JSON pretty-printing works")
    except Exception as e:
        print(f"⚠ Rich JSON not available or error: {e}")

def test_parameter_logging():
    """Test parameter logging."""
    print("\n=== Test 5: Parameter Logging ===")
    Decologr.parameter("User ID", 12345)
    Decologr.parameter("Settings", {"theme": "dark", "lang": "en"})
    print("✓ Parameter logging works")

def test_rich_parameter_display():
    """Test Rich-enhanced parameter display."""
    print("\n=== Test 5b: Rich Parameter Display ===")
    try:
        # Test dictionary with Rich table
        print("Testing dictionary (should show as Rich table):")
        config_dict = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "mydb"
            },
            "cache": {
                "enabled": True,
                "ttl": 3600
            },
            "features": ["auth", "logging", "api"]
        }
        Decologr.parameter("Configuration", config_dict, use_rich=True)
        
        # Test nested list with Rich tree
        print("\nTesting nested list (should show as Rich tree):")
        nested_data = [
            {"id": 1, "name": "Alice", "roles": ["admin", "user"]},
            {"id": 2, "name": "Bob", "roles": ["user"]},
            {"id": 3, "name": "Charlie", "roles": ["guest"]}
        ]
        Decologr.parameter("Users", nested_data, use_rich=True)
        
        # Test simple list
        print("\nTesting simple list:")
        simple_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        Decologr.parameter("Numbers", simple_list, use_rich=True)
        
        print("✓ Rich parameter display works")
    except Exception as e:
        print(f"⚠ Rich parameter display not available or error: {e}")

def test_header_message():
    """Test header message."""
    print("\n=== Test 6: Header Message ===")
    Decologr.header_message("Test Section")
    print("✓ Header message works")

def test_rich_header_messages():
    """Test Rich-enhanced header messages."""
    print("\n=== Test 6b: Rich Header Messages ===")
    try:
        # Test different log levels with Rich panels
        print("Testing INFO level header:")
        Decologr.header_message("Starting Application", level=logging.INFO, use_rich=True)
        
        print("\nTesting WARNING level header:")
        Decologr.header_message("Configuration Warning", level=logging.WARNING, use_rich=True)
        
        print("\nTesting ERROR level header:")
        Decologr.header_message("Critical Error Section", level=logging.ERROR, use_rich=True)
        
        print("\nTesting with custom title:")
        Decologr.header_message("Custom Section", title="[bold cyan]Custom Title[/bold cyan]", use_rich=True)
        
        print("✓ Rich header messages work")
    except Exception as e:
        print(f"⚠ Rich header messages not available or error: {e}")

def test_rich_tracebacks():
    """Test Rich traceback formatting."""
    print("\n=== Test 7: Rich Traceback Formatting ===")
    try:
        # Test error with exception
        print("Testing error with exception (should show Rich traceback):")
        try:
            result = 1 / 0
        except ZeroDivisionError as e:
            Decologr.error("Division by zero occurred", exception=e, use_rich_traceback=True)
        
        # Test warning with exception
        print("\nTesting warning with exception:")
        try:
            int("not a number")
        except ValueError as e:
            Decologr.warning("Invalid number format", exception=e, use_rich_traceback=True)
        
        # Test log_exception function
        print("\nTesting log_exception function:")
        try:
            raise KeyError("Missing key 'test'")
        except KeyError as e:
            log_exception(e, "Failed to access configuration", use_rich_traceback=True)
        
        print("✓ Rich traceback formatting works")
    except Exception as e:
        print(f"⚠ Rich traceback not available or error: {e}")

if __name__ == "__main__":
    print("Testing decologr Rich Integration")
    print("=" * 50)
    
    test_basic_logging()
    test_rich_logging()
    test_auto_detect_rich()
    test_json_logging()
    test_json_pretty_printing()
    test_parameter_logging()
    test_rich_parameter_display()
    test_header_message()
    test_rich_header_messages()
    test_rich_tracebacks()
    
    print("\n" + "=" * 50)
    print("All tests completed!")
