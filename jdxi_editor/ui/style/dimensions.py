"""
class JDXIDimensions

Class to store dimensions of a Roland JDXi instrument

# Example usage:
----------------
>>> print(JDXi.Dimensions.INSTRUMENT.HEIGHT)
400
>>> print(JDXi.Dimensions.INSTRUMENT.WIDTH)
1000
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


class IconDimensions:
    """Icon Dimensions"""

    SIZE_SMALL = 0.7
    WIDTH = 30
    HEIGHT = 30


class DigitalEditorDimensions:
    """Digital Filter Dimensions"""

    SPACING = 5
    MARGINS = (5, 15, 5, 5)


class BasicEditorDimensions:
    """Basic Editor Dimensions"""

    IMAGE_HEIGHT = 150
    WIDTH = 550
    HEIGHT = 550


class DrumEditorDimensions:
    """Drum Editor Dimensions"""

    WIDTH = 1100
    HEIGHT = 800
    PARTIAL_TAB_MIN_WIDTH = (
        400  # Minimum width for drum partial tabs to match WMT width
    )


class WaveformIconDimensions:
    """Waveform Icon Dimensions"""

    WIDTH = 60
    HEIGHT = 30


class SplashScreenDimensions:
    """Splash screen dimensions"""

    HEIGHT = 540
    WIDTH = 850
    IMAGE_WIDTH = 360
    IMAGE_HEIGHT = 220


class ChartDimensions:
    """Chart Dimensions"""

    POINT_SIZE = 2


class InstrumentDimensions:
    """Instrument Dimensions"""

    MARGIN = 15
    HEIGHT = 400
    WIDTH = 1000


class EditorDimensions:
    """EditorDimensions"""

    MINIMUM_HEIGHT = 250


class ArpDimensions:
    """ArpDimensions"""

    MARGIN = 5
    SPACING = 20
    X = 120
    Y = 125
    WIDTH = 120
    HEIGHT = 100


class AnalogEditorDimensions:
    """Analog Editor Dimensions"""

    MIN_WIDTH = 330
    MIN_HEIGHT = 330
    WIDTH = 950
    HEIGHT = 600


class LEDDisplayDimensions:
    """LED display area (enlarged for 2 rows)"""

    WIDTH = 210
    HEIGHT = 70
    X = InstrumentDimensions.MARGIN + 20
    Y = InstrumentDimensions.MARGIN + 35


class DigitalTitleDimensions:
    """
    Digital Title Dimensions
    LED title area (enlarged for 2 rows)"""

    WIDTH = 330
    HEIGHT = 70


class PWMWidgetDimensions:
    """PWM Widget Dimensions"""

    X = 100
    Y = 100
    WIDTH = 300
    HEIGHT = 500


class TitleDimensions:
    """Title above display (moved down)"""

    X = InstrumentDimensions.MARGIN + 20
    Y = InstrumentDimensions.MARGIN
    WIDTH = 200
    HEIGHT = 50


class KeyboardDimensions:
    """Keyboard Dimensions"""

    # Keyboard
    HEIGHT = 127
    WIDTH = 800


class SequencerGridDimensions:
    """Sequencer Grid Dimensions"""

    # --- Sequencer grid
    WIDTH = 300
    HEIGHT = 30


class SequencerContainerDimensions:
    """Sequencer container"""

    X = InstrumentDimensions.MARGIN + 520
    Y = InstrumentDimensions.MARGIN + 155
    WIDTH = 500
    HEIGHT = 80


class SequencerDimensions:
    """Sequencer Dimensions"""

    # --- Sequencer steps

    STEPS = 16
    STEP_SIZE = 18
    SQUARE_SIZE = 25
    # Sequencer above keyboard
    Y_WINDOWS = (
        InstrumentDimensions.HEIGHT - KeyboardDimensions.HEIGHT + 20
    )  # Windows has a menu across the top
    Y_NON_WINDOWS = (
        InstrumentDimensions.HEIGHT - KeyboardDimensions.HEIGHT + 20
    )  # Keep same distance above keyboard
    WIDTH = 440  # # Use roughly half keyboard width
    X = InstrumentDimensions.WIDTH - InstrumentDimensions.MARGIN - WIDTH
    GRID: SequencerGridDimensions = SequencerGridDimensions
    # --- Sequencer container
    CONTAINER: SequencerContainerDimensions = SequencerContainerDimensions


class SliderContainerDimensions:
    """Slider Container Dimensions"""

    WIDTH = 360
    HEIGHT = 120 + 20  # Height = SliderDimensions Height


class SliderDimensions:
    """Slider Dimensions"""

    X = 515
    Y = InstrumentDimensions.MARGIN
    HEIGHT = 120
    CONTAINER: SliderContainerDimensions = SliderContainerDimensions


class PartsDimensions:
    """Parts container"""

    X = LEDDisplayDimensions.X + LEDDisplayDimensions.WIDTH + 10
    Y = InstrumentDimensions.MARGIN
    WIDTH = 180
    HEIGHT = 220


class EffectsButtonDimensions:
    """Effects Button Dimensions"""

    X = 910
    Y = InstrumentDimensions.MARGIN
    WIDTH = 80
    HEIGHT = 120


class ToneButtonDimensions:
    """Tone button dimensions"""

    X = 385
    Y = InstrumentDimensions.MARGIN + 75
    WIDTH = 150
    HEIGHT = 80


class ProgramButtonDimensions:
    """Program buttons"""

    X = 385
    Y = InstrumentDimensions.MARGIN + 15
    WIDTH = 150
    HEIGHT = 80


class OctaveButtonDimensions:
    """Octave Button Dimensions"""

    X = InstrumentDimensions.MARGIN + 10
    Y = 125
    WIDTH = 120
    HEIGHT = 100


class JDXiDimensions:
    """
    A class to store dimensions for the JD-Xi editor UI.
    """

    # --- Icons
    ICON: IconDimensions = IconDimensions
    WAVEFORM_ICON: WaveformIconDimensions = WaveformIconDimensions

    # --- Splash screen
    SPLASH: SplashScreenDimensions = SplashScreenDimensions

    # --- Editor Windows
    INSTRUMENT: InstrumentDimensions = InstrumentDimensions
    EDITOR: EditorDimensions = EditorDimensions
    EDITOR_DIGITAL: DigitalEditorDimensions = DigitalEditorDimensions
    EDITOR_BASIC: BasicEditorDimensions = BasicEditorDimensions
    EDITOR_ANALOG: AnalogEditorDimensions = AnalogEditorDimensions
    EDITOR_DRUM: DrumEditorDimensions = DrumEditorDimensions
    ANALOG = AnalogDimensions
    ARPEGGIATOR: ArpDimensions = ArpDimensions

    # --- Widgets
    PWM_WIDGET: PWMWidgetDimensions = PWMWidgetDimensions
    CHART: ChartDimensions = ChartDimensions
    LED: LEDDisplayDimensions = LEDDisplayDimensions
    DIGITAL_TITLE: DigitalTitleDimensions = DigitalTitleDimensions
    TITLE: TitleDimensions = TitleDimensions
    KEYBOARD: KeyboardDimensions = KeyboardDimensions
    SEQUENCER: SequencerDimensions = SequencerDimensions
    SLIDER: SliderDimensions = SliderDimensions
    PARTS: PartsDimensions = PartsDimensions
    OCTAVE: OctaveButtonDimensions = OctaveButtonDimensions
    PROGRAM: ProgramButtonDimensions = ProgramButtonDimensions
    TONE: ToneButtonDimensions = ToneButtonDimensions
    EFFECTS: EffectsButtonDimensions = EffectsButtonDimensions
