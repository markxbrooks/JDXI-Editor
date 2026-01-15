"""
class JDXIDimensions

Class to store dimensions of a Roland JDXi instrument

# Example usage:
----------------
>>> print(JDXIDimensions.HEIGHT)
>>> print(JDXIDimensions.DISPLAY_WIDTH)

"""


class DigitalDimensions:
    """Digital Dimensions"""
    SPACING = 5 
    MARGIN = 5
    MIN_CONTROL_WIDTH = 20
    MIN_CONTROL_HEIGHT = 14
    MIN_WIDTH = 850
    MIN_HEIGHT = 300
    WIDTH = 1030
    HEIGHT = 600
    

class AnalogDimensions:
    """Analog Editor Dimensions"""
    SPACING = 4
    MARGIN = 5
    MIN_CONTROL_WIDTH = 20
    MIN_CONTROL_HEIGHT = 14


class JDXiDimensions:
    """
    A class to store dimensions for the JD-Xi editor UI.
    """
    ICON_WIDTH = 30
    ICON_HEIGHT = 30
    DIGITAL_FILTER_SPACING = 5
    DIGITAL_FILTER_MARGINS = (5, 15, 5, 5)
    BASIC_EDITOR_IMAGE_HEIGHT = 150
    BASIC_EDITOR_WIDTH = 550
    BASIC_EDITOR_HEIGHT = 550
    DRUM_WIDTH = 1100
    DRUM_HEIGHT = 800
    ANALOG = AnalogDimensions
    
    WAVEFORM_ICON_WIDTH = 60
    WAVEFORM_ICON_HEIGHT = 30

    SPLASH_HEIGHT = 540
    SPLASH_WIDTH = 850
    CHART_POINT_SIZE = 2
    EDITOR_MINIMUM_HEIGHT = 250
    HEIGHT = 400
    WIDTH = 1000

    MARGIN = 15
    
    ARP_MARGIN = 5
    ARP_SPACING = 20

    # LED display area (enlarged for 2 rows)
    DISPLAY_WIDTH = 210
    DISPLAY_HEIGHT = 70
    DISPLAY_X = MARGIN + 20
    DISPLAY_Y = MARGIN + 35

    # LED title area (enlarged for 2 rows)
    DIGITAL_TITLE_WIDTH = 330
    DIGITAL_TITLE_HEIGHT = 70

    EDITOR_DIGITAL_SPLITTER_SIZES = [
        250,
        450,
    ]  # More room for top section (Presets/Partials)
    EDITOR_DRUM_ANALOG_SPLITTER_SIZES = [200, 400]
    EDITOR_ANALOG_MIN_WIDTH = 330
    EDITOR_ANALOG_MIN_HEIGHT = 330
    EDITOR_ANALOG_WIDTH = 950
    EDITOR_ANALOG_HEIGHT = 600

    PWM_WIDGET_X = 100
    PWM_WIDGET_Y = 100
    PWM_WIDGET_WIDTH = 300
    PWM_WIDGET_HEIGHT = 500

    # Title above display (moved down)
    TITLE_X = DISPLAY_X
    TITLE_Y = MARGIN
    TITLE_WIDTH = 200
    TITLE_HEIGHT = 50

    # Keyboard
    WHITE_KEY_HEIGHT = 127
    KEYBOARD_WIDTH = 800

    # Sequencer above keyboard
    SEQUENCER_Y_WINDOWS = (
        HEIGHT - WHITE_KEY_HEIGHT + 20
    )  # Windows has a menu across the top
    SEQUENCER_Y_NON_WINDOWS = (
        HEIGHT - WHITE_KEY_HEIGHT + 20
    )  # Keep same distance above keyboard
    SEQUENCER_WIDTH = 440  # # Use roughly half keyboard width
    SEQUENCER_X = WIDTH - MARGIN - SEQUENCER_WIDTH  # Align with right edge of keyboard

    # Sequencer grid
    SEQUENCER_STEPS = 16
    SEQUENCER_STEP_SIZE = 18
    SEQUENCER_GRID_WIDTH = 300
    SEQUENCER_GRID_HEIGHT = 30
    SEQUENCER_SQUARE_SIZE = 25

    # Sequencer container
    SEQUENCER_CONTAINER_X = MARGIN + 520
    SEQUENCER_CONTAINER_Y = MARGIN + 155
    SEQUENCER_CONTAINER_WIDTH = 500
    SEQUENCER_CONTAINER_HEIGHT = 80

    # Sliders
    SLIDER_X = 515
    SLIDER_Y = MARGIN
    SLIDER_CONTAINER_WIDTH = 360
    SLIDER_HEIGHT = 120
    SLIDER_CONTAINER_HEIGHT = SLIDER_HEIGHT + 20

    # Parts container
    PARTS_X = DISPLAY_X + DISPLAY_WIDTH + 10
    PARTS_Y = MARGIN
    PARTS_WIDTH = 180
    PARTS_HEIGHT = 220

    # Octave buttons
    OCTAVE_X = MARGIN + 10
    OCTAVE_Y = 125
    OCTAVE_WIDTH = 120
    OCTAVE_HEIGHT = 100

    # Arpeggiator buttons
    ARPEGGIATOR_X = 120
    ARPEGGIATOR_Y = 125
    ARPEGGIATOR_WIDTH = 120
    ARPEGGIATOR_HEIGHT = 100

    # Program buttons
    PROGRAM_X = 385
    PROGRAM_Y = MARGIN + 15
    PROGRAM_WIDTH = 150
    PROGRAM_HEIGHT = 80

    # Tone buttons
    TONE_X = 385
    TONE_Y = MARGIN + 75
    TONE_WIDTH = 150
    TONE_HEIGHT = 80

    # Effects buttons
    EFFECTS_X = 910
    EFFECTS_Y = MARGIN
    EFFECTS_WIDTH = 80
    EFFECTS_HEIGHT = 120

    SCROLL_AREA_HEIGHT = 100
    DRUM_PARTIAL_TAB_MIN_WIDTH = (
        400  # Minimum width for drum partial tabs to match WMT width
    )
