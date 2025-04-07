"""
class JDXIDimensions

Class to store dimensions of a Roland JDXi instrument

# Example usage:
# print(JDXIDimensions.HEIGHT)
# print(JDXIDimensions.DISPLAY_WIDTH)
"""
JDXI_HEIGHT = 400

JDXI_WIDTH = 1000

JDXI_WHITE_KEY_HEIGHT = 127

JDXI_KEYBOARD_WIDTH = 800

JDXI_MARGIN = 15


# LED display area (enlarged for 2 rows)
JDXI_DISPLAY_WIDTH = 180
JDXI_DISPLAY_HEIGHT = 70
JDXI_DISPLAY_X = JDXI_MARGIN + 20
JDXI_DISPLAY_Y = JDXI_MARGIN + 35
# Title above display (moved down)
JDXI_TITLE_X = JDXI_DISPLAY_X
JDXI_TITLE_Y = JDXI_MARGIN


class JDXIDimensions:
    """
    A class to store dimensions for the JD-Xi editor UI.
    """

    HEIGHT = 400
    WIDTH = 1000

    MARGIN = 15

    # LED display area (enlarged for 2 rows)
    DISPLAY_WIDTH = 180
    DISPLAY_HEIGHT = 70
    DISPLAY_X = MARGIN + 20
    DISPLAY_Y = MARGIN + 35

    # Title above display (moved down)
    TITLE_X = DISPLAY_X
    TITLE_Y = MARGIN
    
    # Keyboard
    WHITE_KEY_HEIGHT = 127
    KEYBOARD_WIDTH = 800

    # Sequencer above keyboard
    SEQUENCER_Y_WINDOWS = HEIGHT - WHITE_KEY_HEIGHT + 20  # Windows has a menu across the top
    SEQUENCER_Y_NON_WINDOWS = HEIGHT - WHITE_KEY_HEIGHT - 20  # Keep same distance above keyboard
    SEQUENCER_WIDTH = KEYBOARD_WIDTH * 0.53 # # Use roughly half keyboard width
    SEQUENCER_X = WIDTH - MARGIN - SEQUENCER_WIDTH  # Align with right edge of keyboard
    SEQUENCER_STEPS = 16
    SEQUENCER_SQUARE_SIZE = 18

    # Sliders
    SLIDER_HEIGHT = 100

    # Parts container
    PARTS_X = DISPLAY_X + DISPLAY_WIDTH + 35
    PARTS_Y = int(DISPLAY_Y - (HEIGHT * 0.15))
