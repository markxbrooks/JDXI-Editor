"""
Common Section
"""

from typing import Callable, Optional

from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.base.common import BaseCommonSection
from jdxi_editor.ui.editors.base.layout.spec import LayoutSpec
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SliderSpec, SwitchSpec


class DigitalCommonSection(BaseCommonSection):
    """Digital Common Section"""

    def __init__(
            self,
            controls: dict = None,
            address: Optional[RolandSysExAddress] = None,
            send_midi_parameter: Optional[Callable] = None,
            midi_helper: Optional[MidiIOHelper] = None,
    ):
        """
        Initialize the DigitalCommonSection

        :param controls: dict Controls dictionary
        :param address: Optional[RolandSysExAddress] MIDI address for parameter sending
        :param send_midi_parameter: Optional[Callable] Function to send MIDI parameters
        :param midi_helper: Optional[MidiIOHelper] MIDI helper instance
        """
        self.SLIDER_GROUPS: LayoutSpec = self._build_layout_spec()
        self.OTHER_SWITCHES = self.SLIDER_GROUPS.misc
        self.PORTAMENTO_SWITCHES = self.SLIDER_GROUPS.switches
        self.COMBO_BOXES = self.SLIDER_GROUPS.combos

        super().__init__(
            controls=controls,
            icons_row_type=IconType.GENERIC,
            midi_helper=midi_helper,
            send_midi_parameter=send_midi_parameter,
            analog=False,
        )
        self.address: RolandSysExAddress = address
        self.widgets: dict = {}
        self.build_widgets()
        self.setup_ui()

    # ------------------------------------------------------------
    # Widget construction
    # ------------------------------------------------------------

    def build_widgets(self) -> None:
        """Build all the necessary widgets for the digital common section."""
        self.widgets = {
            "sliders": self._build_sliders(self.SLIDER_GROUPS.controls),
            "portamento_switches": self._build_switches(self.SLIDER_GROUPS.switches),
            "octave_shift": self._build_combo_boxes(self.SLIDER_GROUPS.combos),
            "other_switches": self._build_switches(self.SLIDER_GROUPS.misc),
        }
        # Register widgets in the shared controls dict so the editor's
        # _update_common_controls can find them when COMMON SysEx arrives.
        if self.controls is not None:
            for spec, w in zip(
                    self.SLIDER_GROUPS.controls, self.widgets["sliders"]
            ):
                self.controls[spec.param] = w
            for spec, w in zip(
                    self.SLIDER_GROUPS.switches, self.widgets["portamento_switches"]
            ):
                self.controls[spec.param] = w
            for spec, w in zip(self.SLIDER_GROUPS.combos, self.widgets["octave_shift"]):
                self.controls[spec.param] = w
            for spec, w in zip(
                    self.SLIDER_GROUPS.misc, self.widgets["other_switches"]
            ):
                self.controls[spec.param] = w

    # ------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------

    def _setup_ui(self) -> None:
        pass  # Don't make a QTabWidget

    def setup_ui(self) -> None:
        """setup ui"""
        widget_rows = [
            self.widgets["octave_shift"],
            self.widgets["other_switches"][:1],  # Mono switch
            self.widgets["sliders"],
            self.widgets["other_switches"][1:3],  # Ring and Unison switches
            [self.widgets["other_switches"][3]],  # Unison size
            self.widgets["portamento_switches"],
        ]
        self._add_group_with_widget_rows(label="Common", rows=widget_rows)

    def _build_layout_spec(self) -> LayoutSpec:
        """build Analog Oscillator Layout Spec"""
        S = self.SYNTH_SPEC
        pitch = [
            SliderSpec(
                Digital.Common.PITCH_BEND_UP, Digital.Display.Name.PITCH_BEND_UP
            ),
            SliderSpec(
                Digital.Common.PITCH_BEND_DOWN, Digital.Display.Name.PITCH_BEND_DOWN
            ),
            SliderSpec(Digital.Common.TONE_LEVEL, Digital.Display.Name.TONE_LEVEL),
            SliderSpec(
                Digital.Common.PORTAMENTO_TIME, Digital.Display.Name.PORTAMENTO_TIME
            ),
            SliderSpec(Digital.Common.ANALOG_FEEL, Digital.Display.Name.ANALOG_FEEL),
            SliderSpec(Digital.Common.WAVE_SHAPE, Digital.Display.Name.WAVE_SHAPE),
        ]
        portamento_switches = [
            SwitchSpec(
                Digital.Common.PORTAMENTO_SWITCH,
                Digital.Display.Name.PORTAMENTO_SWITCH,
                Digital.Display.Options.PORTAMENTO_SWITCH,
            ),
            SwitchSpec(
                Digital.Common.PORTAMENTO_MODE,
                Digital.Display.Name.PORTAMENTO_MODE,
                Digital.Display.Options.PORTAMENTO_MODE,
            ),
            SwitchSpec(
                Digital.Common.LEGATO_SWITCH,
                Digital.Display.Name.LEGATO_SWITCH,
                Digital.Display.Options.LEGATO_SWITCH,
            ),

        ]
        combos = [
            ComboBoxSpec(
                Digital.Common.OCTAVE_SHIFT,
                Digital.Display.Name.OCTAVE_SHIFT,
                Digital.Display.Options.OCTAVE_SHIFT,
                [61, 62, 63, 64, 65, 66, 67],
            ),

        ]
        other_switches = [
            SwitchSpec(
                Digital.Common.MONO_SWITCH,
                Digital.Display.Name.MONO_SWITCH,
                Digital.Display.Options.MONO_SWITCH,
            ),
            SwitchSpec(
                Digital.Common.RING_SWITCH,
                Digital.Display.Name.RING_SWITCH,
                Digital.Display.Options.RING_SWITCH,
            ),
            SwitchSpec(
                Digital.Common.UNISON_SWITCH,
                Digital.Display.Name.UNISON_SWITCH,
                Digital.Display.Options.UNISON_SWITCH,
            ),
            SwitchSpec(
                Digital.Common.UNISON_SIZE,
                Digital.Display.Name.UNISON_SIZE,
                Digital.Display.Options.UNISON_SIZE,
            ),
        ]
        return LayoutSpec(controls=pitch, switches=portamento_switches, combos=combos, misc=other_switches)
