"""
MOD LFO section of the digital partial editor.
"""

from typing import Callable, Literal

from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.parameter.digital import DigitalPartialParam
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.ui.editors.base.lfo import BaseLFOSection
from jdxi_editor.ui.editors.base.lfo.layout import LFOLayoutSpec
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.spec import SliderSpec, SwitchSpec


class DigitalModLFOSection(BaseLFOSection):
    """MOD LFO section for the digital partial editor."""

    SYNTH_SPEC = Digital

    rate_tab_label = "Rate and Rate Ctrl"

    def __init__(
        self,
        on_parameter_changed: Callable,
        send_midi_parameter: Callable = None,
        midi_helper=None,
        address: RolandSysExAddress = None,
        icons_row_type: str = IconType.ADSR,
        analog: bool = False,
    ):
        """
        Initialize the DigitalModLFOSection

        :param on_parameter_changed: Callable
        :param send_midi_parameter: Callable to send MIDI parameter updates
        :param midi_helper: MidiIOHelper for MIDI communication
        :param address: RolandSysExAddress for this partial (required for sending MIDI)
        """
        self._on_parameter_changed = on_parameter_changed
        self.wave_shape_buttons = {}  # Dictionary to store Mod LFO shape buttons

        super().__init__(
            icons_row_type=icons_row_type,
            analog=analog,
            send_midi_parameter=send_midi_parameter,
            address=address,
            midi_helper=midi_helper,
        )
        self.midi_helper = midi_helper
        self.wave_shape_param: Literal[DigitalPartialParam.MOD_LFO_SHAPE] = (
            DigitalPartialParam.MOD_LFO_SHAPE
        )
        self.build_widgets()
        self.setup_ui()

    def _build_layout_spec(self) -> LFOLayoutSpec:
        """Layout spec using MOD_LFO_* params so controls dict gets MOD_LFO_* keys."""
        P = self.SYNTH_SPEC.Param
        D = self.SYNTH_SPEC.Display
        switches = [
            SwitchSpec(
                P.MOD_LFO_TEMPO_SYNC_SWITCH,
                D.Name.MOD_LFO_TEMPO_SYNC_SWITCH,
                D.Options.MOD_LFO_TEMPO_SYNC_SWITCH,
            ),
            SwitchSpec(
                P.MOD_LFO_TEMPO_SYNC_NOTE,
                D.Name.MOD_LFO_TEMPO_SYNC_NOTE,
                D.Options.MOD_LFO_TEMPO_SYNC_NOTE,
            ),
        ]
        depths = [
            SliderSpec(P.MOD_LFO_PITCH_DEPTH, D.Name.MOD_LFO_PITCH_DEPTH),
            SliderSpec(P.MOD_LFO_FILTER_DEPTH, D.Name.MOD_LFO_FILTER_DEPTH),
            SliderSpec(P.MOD_LFO_AMP_DEPTH, D.Name.MOD_LFO_AMP_DEPTH),
            SliderSpec(P.MOD_LFO_PAN, D.Name.MOD_LFO_PAN),
        ]
        rate = [
            SliderSpec(P.MOD_LFO_RATE, D.Name.MOD_LFO_RATE),
            SliderSpec(P.MOD_LFO_RATE_CTRL, D.Name.MOD_LFO_RATE_CTRL),
        ]
        return LFOLayoutSpec(switches=switches, depth_sliders=depths, rate_sliders=rate)
