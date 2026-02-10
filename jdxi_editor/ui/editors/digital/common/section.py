"""
Common Section
"""

from typing import Callable, Optional

from jdxi_editor.midi.data.address.address import JDXiSysExAddress
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.base.common import BaseCommonSection
from jdxi_editor.ui.editors.digital.common.spec import CommonWidgetSpec
from jdxi_editor.ui.editors.digital.common.widget import CommonEditorWidgets
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SliderSpec, SwitchSpec


class DigitalCommonSection(BaseCommonSection):
    """Digital Common Section"""

    def __init__(
            self,
            controls: dict = None,
            address: Optional[JDXiSysExAddress] = None,
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
        self.spec: CommonWidgetSpec = self._build_layout_spec()
        self.OTHER_SWITCHES = self.spec.other_switches
        self.PORTAMENTO_SWITCHES = self.spec.portamento_switches
        self.COMBO_BOXES = self.spec.octave_shift

        super().__init__(
            controls=controls,
            icons_row_type=IconType.GENERIC,
            midi_helper=midi_helper,
            send_midi_parameter=send_midi_parameter,
            analog=False,
        )
        self.address: JDXiSysExAddress = address
        self.widgets: CommonEditorWidgets | None = None
        self.build_widgets()
        self.setup_ui()

    # ------------------------------------------------------------
    # Widget construction
    # ------------------------------------------------------------

    def build_widgets(self) -> None:
        """Build all the necessary widgets for the digital common section."""
        self.widgets = CommonEditorWidgets(pitch=self._build_sliders(self.spec.pitch),
                                           portamento=self._build_switches(self.spec.portamento_switches),
                                           octave_shift=self._build_combo_boxes(self.spec.octave_shift),
                                           other_switches=self._build_switches(self.spec.other_switches),
                                           )
        # Register widgets in the shared controls dict so the editor's
        # _update_common_controls can find them when COMMON SysEx arrives.
        if self.controls is not None:
            for spec, w in zip(self.spec.pitch, self.widgets.pitch):
                self.controls[spec.param] = w
            for spec, w in zip(
                    self.spec.portamento_switches, self.widgets.portamento
            ):
                self.controls[spec.param] = w
            for spec, w in zip(self.spec.octave_shift, self.widgets.octave_shift):
                self.controls[spec.param] = w
            for spec, w in zip(self.spec.other_switches, self.widgets.other_switches):
                self.controls[spec.param] = w

    # ------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------

    def _setup_ui(self) -> None:
        pass  # Don't make a QTabWidget

    def setup_ui(self) -> None:
        """setup ui"""
        widget_rows = [
            self.widgets.octave_shift,
            self.widgets.other_switches[:1],  # Mono switch
            self.widgets.pitch,
            self.widgets.other_switches[1:3],  # Ring and Unison switches
            [self.widgets.other_switches[3]],  # Unison size
            self.widgets.portamento,
        ]
        self._add_group_with_widget_rows(label="Common", rows=widget_rows)

    def _build_layout_spec(self) -> CommonWidgetSpec:
        """build Analog Oscillator Layout Spec"""
        S = self.SYNTH_SPEC
        pitch = [
            SliderSpec(S.Common.PITCH_BEND_UP, S.Common.PITCH_BEND_UP.display_name),
            SliderSpec(S.Common.PITCH_BEND_DOWN, S.Common.PITCH_BEND_DOWN.display_name),
            SliderSpec(S.Common.TONE_LEVEL, S.Common.TONE_LEVEL.display_name),
            SliderSpec(S.Common.PORTAMENTO_TIME, S.Common.PORTAMENTO_TIME.display_name),
            SliderSpec(S.Common.ANALOG_FEEL, S.Common.ANALOG_FEEL.display_name),
            SliderSpec(S.Common.WAVE_SHAPE, S.Common.WAVE_SHAPE.display_name),
        ]
        portamento_switches = [
            SwitchSpec(
                S.Common.PORTAMENTO_SWITCH,
                S.Common.PORTAMENTO_SWITCH.display_name,
                Digital.Display.Options.PORTAMENTO_SWITCH,
            ),
            SwitchSpec(
                S.Common.PORTAMENTO_MODE,
                S.Common.PORTAMENTO_MODE.display_name,
                Digital.Display.Options.PORTAMENTO_MODE,
            ),
            SwitchSpec(
                S.Common.LEGATO_SWITCH,
                S.Common.LEGATO_SWITCH.display_name,
                Digital.Display.Options.LEGATO_SWITCH,
            ),
        ]
        octave_shift = [
            ComboBoxSpec(
                S.Common.OCTAVE_SHIFT,
                S.Common.OCTAVE_SHIFT.display_name,
                Digital.Display.Options.OCTAVE_SHIFT,
                [61, 62, 63, 64, 65, 66, 67],
            ),
        ]
        other_switches = [
            SwitchSpec(
                S.Common.MONO_SWITCH,
                S.Common.MONO_SWITCH.display_name,
                Digital.Display.Options.MONO_SWITCH,
            ),
            SwitchSpec(
                S.Common.RING_SWITCH,
                S.Common.RING_SWITCH.display_name,
                Digital.Display.Options.RING_SWITCH,
            ),
            SwitchSpec(
                S.Common.UNISON_SWITCH,
                S.Common.UNISON_SWITCH.display_name,
                Digital.Display.Options.UNISON_SWITCH,
            ),
            SwitchSpec(
                S.Common.UNISON_SIZE,
                S.Common.UNISON_SIZE.display_name,
                Digital.Display.Options.UNISON_SIZE,
            ),
        ]
        return CommonWidgetSpec(
            pitch=pitch,
            portamento_switches=portamento_switches,
            octave_shift=octave_shift,
            other_switches=other_switches,
        )
