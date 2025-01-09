class ARP:
    """Arpeggiator data and constants"""
    
    PATTERNS = [
        "Up",
        "Down", 
        "Up/Down",
        "Random",
        "Note Order",
        "Up x2",
        "Down x2",
        "Up&Down x2"
    ]
    
    NOTE_VALUES = [
        "1/4",
        "1/4T",
        "1/8",
        "1/8T", 
        "1/16",
        "1/16T",
        "1/32",
        "1/32T"
    ]
    
    # Parameter ranges
    RANGES = {
        'pattern': (0, 7),
        'octave': (0, 3),
        'accent': (0, 100),
        'rate': (0, 127),
        'duration': (0, 100),
        'shuffle': (0, 100)
    } 