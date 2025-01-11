from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt

class Style:
    """Application styling constants"""
    
    # Main colors
    DARK_RED = "#8B0000"      # Dark red base
    RED = "#B22222"           # Standard red
    LIGHT_RED = "#CD5C5C"     # Indian red
    PALE_RED = "#E9967A"      # Dark salmon
    ORANGE_RED = "#FF4500"    # Orange red
    LIGHT_ORANGE = "#FFA07A"  # Light salmon

    # Basic UI colors
    DARK_BG = "#1E1E1E"
    LIGHT_BG = "#2D2D2D"
    HEADER_BG = RED
    PRESET_BG = DARK_RED

    # Section background colors
    OSC_BG = DARK_RED        # Darkest for oscillators
    MIX_BG = RED             # Mixer sections
    VCF_BG = LIGHT_RED       # Filter sections
    VCA_BG = PALE_RED        # Amplifier sections
    LFO_BG = ORANGE_RED      # LFO sections
    ENV_BG = LIGHT_ORANGE    # Envelope sections
    
    # Envelope-specific backgrounds
    PITCH_ENV_BG = DARK_RED
    VCF_ENV_BG = RED
    VCA_ENV_BG = LIGHT_RED
    
    # Performance section
    PERF_BG = ORANGE_RED
    
    # Effects backgrounds
    FX_BG = RED
    DELAY_BG = LIGHT_RED
    REVERB_BG = PALE_RED
    
    # Drum section
    DRUM_BG = DARK_RED
    DRUM_PAD_BG = LIGHT_RED
    PATTERN_BG = PALE_RED
    COMMON_BG = ORANGE_RED
    
    # Digital synth sections
    DIG_OSC_BG = DARK_RED
    DIG_FILTER_BG = RED
    DIG_AMP_BG = LIGHT_RED
    
    # Additional sections
    COM_BG = DARK_RED       # Common section
    MOD_BG = RED           # Modulation section
    ARP_BG = ORANGE_RED    # Arpeggiator section

    # Main stylesheet
    MAIN_STYLESHEET = """
        * {
            font-family: "Myriad Pro", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }
        QMainWindow {
            background-color: #1E1E1E;
            color: #FFFFFF;
        }
        QLabel {
            color: #FFFFFF;
            font-size: 11px;
        }
        QFrame {
            background-color: #2D2D2D;
            border-radius: 5px;
        }
        QComboBox {
            background-color: #3D3D3D;
            color: #FFFFFF;
            border: 1px solid #555555;
            border-radius: 3px;
            padding: 3px;
            font-size: 11px;
        }
        QComboBox::drop-down {
            border: none;
        }
        QComboBox::down-arrow {
            image: url(resources/down_arrow.png);
        }
        QPushButton {
            background-color: #3D3D3D;
            color: #FFFFFF;
            border: 1px solid #555555;
            border-radius: 3px;
            padding: 5px;
            font-size: 11px;
        }
        QPushButton:hover {
            background-color: #4D4D4D;
        }
        QPushButton:pressed {
            background-color: #2D2D2D;
        }
        QSlider::groove:horizontal {
            border: 1px solid #555555;
            height: 4px;
            background: #3D3D3D;
            margin: 2px 0;
        }
        QSlider::handle:horizontal {
            background: #FFFFFF;
            border: 1px solid #5A5A5A;
            width: 18px;
            margin: -8px 0;
            border-radius: 3px;
        }
    """

    @staticmethod
    def section_header(bg_color):
        """Create section header style"""
        return f"""
            QLabel {{
                background-color: {bg_color};
                color: white;
                padding: 5px;
                font-weight: bold;
                font-size: 12px;
                font-family: "Myriad Pro", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                border-radius: 3px;
            }}
        """ 