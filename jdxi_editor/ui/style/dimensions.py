"""
class JDXIDimensions

Class to store dimensions of a Roland JDXi instrument

# Example usage:
----------------
>>> print(JDXiUIDimensions.INSTRUMENT.HEIGHT)
400
>>> print(JDXiUIDimensions.INSTRUMENT.WIDTH)
1000
"""

from dataclasses import dataclass
from typing import Optional


class ControlMetrics:
    MIN_WIDTH: int = 20
    MIN_HEIGHT: int = 14


@dataclass(frozen=True)
class Margins:
    left: int
    top: int
    right: int
    bottom: int

    def __iter__(self):
        """Make Margins iterable so it can be unpacked with *margins."""
        return iter((self.left, self.top, self.right, self.bottom))


class Dimensions:
    """Dimensions"""

    X: int = 0
    Y: int = 0
    WIDTH: int = 0
    HEIGHT: int = 0

    MARGIN: int = 0
    SPACING: int = 0

    MIN_WIDTH: Optional[int] = None
    MIN_HEIGHT: Optional[int] = None

    MAX_WIDTH: Optional[int] = None
    MAX_HEIGHT: Optional[int] = None

    INIT_WIDTH: Optional[int] = None
    INIT_HEIGHT: Optional[int] = None

    MARGINS: tuple = (5, 5, 5, 5)

    @classmethod
    def right(cls) -> int:
        return cls.X + cls.WIDTH

    @classmethod
    def bottom(cls) -> int:
        return cls.Y + cls.HEIGHT


class DigitalDimensions(Dimensions):
    """Digital Dimensions"""

    SPACING: int = 5
    MARGIN: int = 5
    MIN_CONTROL_WIDTH: int = 20
    MIN_CONTROL_HEIGHT: int = 14
    MIN_WIDTH = 850
    MIN_HEIGHT: int = 300
    WIDTH: int = 1030
    HEIGHT = 600


class AnalogDimensions(Dimensions):
    """Analog Editor Dimensions"""

    SPACING: int = 4
    MARGIN: int = 5
    MIN_CONTROL_WIDTH: int = 20
    MIN_CONTROL_HEIGHT: int = 14


class ComboBoxDimensions(Dimensions):
    """Combo Box Dimensions"""

    WIDTH: int = 425
    HEIGHT: int = 25


class IconDimensions(Dimensions):
    """Icon Dimensions"""

    SCALE_SMALL: float = 0.7
    WIDTH: int = 30
    HEIGHT: int = 30


class SmallIconDimensions(Dimensions):
    """Dimensions of an Icon"""

    WIDTH: int = 20
    HEIGHT: int = 20


class DigitalEditorDimensions(Dimensions):
    """Digital Filter Dimensions"""

    SPACING: int = 5
    MARGINS = Margins(5, 15, 5, 5)
    MIN_WIDTH: Optional[int] = 850
    MIN_HEIGHT: Optional[int] = 300
    INIT_WIDTH: Optional[int] = 1030
    INIT_HEIGHT: Optional[int] = 600


class BasicEditorDimensions(Dimensions):
    """Basic Editor Dimensions"""

    IMAGE_HEIGHT: int = 150
    WIDTH: int = 550
    HEIGHT: int = 550


class DrumEditorDimensions(Dimensions):
    """Drum Editor Dimensions"""

    WIDTH: int = 1100
    HEIGHT: int = 800
    PARTIAL_TAB_MIN_WIDTH = (
        400  # Minimum width for drum partial tabs to match WMT width
    )
    MIN_HEIGHT: Optional[int] = 300


class WaveformIconDimensions(Dimensions):
    """Waveform Icon Dimensions"""

    Icon: SmallIconDimensions = SmallIconDimensions  # Need lots of waveform icons
    WIDTH: int = 80
    HEIGHT: int = 30


class LfoIconDimensions(Dimensions):
    """Lfo Icon Dimensions"""

    WIDTH: int = 20
    HEIGHT: int = 20


class SplashScreenDimensions(Dimensions):
    """Splash screen dimensions (matches splash_screen_540_850.png)"""

    WIDTH: int = 850
    HEIGHT: int = 540
    IMAGE_WIDTH: int = 850
    IMAGE_HEIGHT: int = 540


class ChartMetrics:
    """Chart Metrics"""

    POINT_SIZE: int = 2


class InstrumentDimensions(Dimensions):
    """Instrument Dimensions"""

    MARGIN: int = 15
    HEIGHT: int = 400
    WIDTH: int = 1000


class EditorDimensions(Dimensions):
    """EditorDimensions"""

    HEIGHT: int = 250
    MIN_HEIGHT: int = 250
    MARGINS = (1, 1, 1, 1)


class ArpDimensions(Dimensions):
    """ArpDimensions"""

    MARGIN: int = 5
    SPACING: int = 20
    X: int = 120
    Y: int = 125
    WIDTH: int = 120
    HEIGHT: int = 100


class AnalogEditorDimensions(EditorDimensions):
    """Analog Editor Dimensions"""

    MIN_WIDTH: int = 330
    MIN_HEIGHT: int = 330
    WIDTH: int = 950
    HEIGHT: int = 600
    MARGINS = (1, 1, 1, 1)


class LEDDisplayDimensions(Dimensions):
    """LED digital area (enlarged for 2 rows)"""

    WIDTH: int = 210
    HEIGHT: int = 70
    X = InstrumentDimensions.MARGIN + 20
    Y = InstrumentDimensions.MARGIN + 35


class DigitalTitleDimensions(Dimensions):
    """
    Digital Title Dimensions
    LED title area (enlarged for 2 rows)"""

    WIDTH: int = 330
    HEIGHT: int = 70


class PWMWidgetDimensions(Dimensions):
    """PWM Widget Dimensions"""

    X: int = 100
    Y: int = 100
    WIDTH: int = 300
    HEIGHT: int = 500


class TitleDimensions(Dimensions):
    """Title above digital (moved down)"""

    X = InstrumentDimensions.MARGIN + 20
    Y = InstrumentDimensions.MARGIN
    WIDTH: int = 200
    HEIGHT: int = 50


class KeyboardDimensions(Dimensions):
    """Keyboard Dimensions"""

    # Keyboard
    HEIGHT: int = 127
    WIDTH = 800


class SequencerGridDimensions(Dimensions):
    """Sequencer Grid Dimensions"""

    # --- Sequencer grid
    WIDTH: int = 300
    HEIGHT: int = 30


class SequencerContainerDimensions(Dimensions):
    """Sequencer container"""

    X = InstrumentDimensions.MARGIN + 520
    Y = InstrumentDimensions.MARGIN + 155
    WIDTH: int = 500
    HEIGHT: int = 80


class SequencerDimensions(Dimensions):
    """Sequencer Dimensions"""

    # --- Sequencer steps

    STEPS: int = 16
    STEP_SIZE: int = 18
    SQUARE_SIZE: int = 25
    LARGE_SQUARE_SIZE: int = 40
    # Sequencer above keyboard
    Y_WINDOWS = (
        InstrumentDimensions.HEIGHT - KeyboardDimensions.HEIGHT + 20
    )  # Windows has a menu across the top
    Y_NON_WINDOWS = (
        InstrumentDimensions.HEIGHT - KeyboardDimensions.HEIGHT + 20
    )  # Keep same distance above keyboard
    WIDTH: int = 440  # # Use roughly half keyboard width
    X = InstrumentDimensions.WIDTH - InstrumentDimensions.MARGIN - WIDTH
    GRID: SequencerGridDimensions = SequencerGridDimensions
    # --- Sequencer container
    CONTAINER: SequencerContainerDimensions = SequencerContainerDimensions


class SliderContainerDimensions(Dimensions):
    """Slider Container Dimensions"""

    WIDTH: int = 360
    HEIGHT: int = 120 + 20  # Height = SliderDimensions Height


class SliderDimensions(Dimensions):
    """Slider Dimensions"""

    X: int = 515
    Y: int = InstrumentDimensions.MARGIN
    HEIGHT: int = 120
    CONTAINER: SliderContainerDimensions = SliderContainerDimensions


class PartsDimensions(Dimensions):
    """Parts container"""

    X = LEDDisplayDimensions.right() + 10
    Y = InstrumentDimensions.MARGIN
    WIDTH: int = 180
    HEIGHT: int = 220


class EffectsButtonDimensions(Dimensions):
    """Effects Button Dimensions"""

    X = 910
    Y = InstrumentDimensions.MARGIN
    WIDTH = 80
    HEIGHT: int = 120


class RoundButtonDimensions(Dimensions):
    """Button Dimensions"""

    WIDTH: int = 30
    HEIGHT: int = 30


class ToneButtonDimensions(Dimensions):
    """Tone button dimensions"""

    X: int = 385
    Y = InstrumentDimensions.MARGIN + 75
    WIDTH: int = 150
    HEIGHT = 80


class ProgramButtonDimensions(Dimensions):
    """Program buttons"""

    X: int = 385
    Y = InstrumentDimensions.MARGIN + 15
    WIDTH: int = 150
    HEIGHT = 80


class OctaveButtonDimensions(Dimensions):
    """Octave Button Dimensions"""

    X = InstrumentDimensions.MARGIN + 10
    Y: int = 125
    WIDTH: int = 120
    HEIGHT: int = 100


class MidiConfig(Dimensions):
    """Midi Config Dimensions"""

    WIDTH = 300
    HEIGHT = 300


class SliderValueLabelDimensions(Dimensions):
    """Slider label dimensions"""

    MIN_WIDTH = 20


class VerticalSliderDimensions(Dimensions):
    """Slider Dimensions"""

    label = SliderValueLabelDimensions
    HEIGHT = 180

    MIN_WIDTH = 80
    MAX_WIDTH = 100


class HorizontalSliderDimensions(Dimensions):
    """Slider Dimensions"""

    label = SliderValueLabelDimensions
    HEIGHT = 180
    MIN_HEIGHT = 50
    MAX_HEIGHT = 60

    MIN_WIDTH = 80
    MAX_WIDTH = 100


class JDXiUIDimensions(Dimensions):
    """
    A class to store dimensions for the JD-Xi editor UI.
    """

    # --- Icons
    slider_vertical = VerticalSliderDimensions
    slider_horizontal = HorizontalSliderDimensions
    Icon: IconDimensions = IconDimensions
    Combo: ComboBoxDimensions = ComboBoxDimensions
    WaveformIcon: WaveformIconDimensions = WaveformIconDimensions
    LFOIcon: LfoIconDimensions = LfoIconDimensions

    # --- Splash screen
    SPLASH: SplashScreenDimensions = SplashScreenDimensions

    # Config
    Config: MidiConfig = MidiConfig

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
    BUTTON_ROUND: RoundButtonDimensions = RoundButtonDimensions
    CHART: ChartMetrics = ChartMetrics
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
