"""
LFO section of the digital partial editor.
"""

from typing import Callable

from PySide6.QtWidgets import QPushButton, QTabWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import JDXiSysExAddress
from jdxi_editor.midi.data.parameter.analog.spec import AnalogWave
from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.midi.data.parameter.digital.spec import DigitalWave
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.base.lfo.group import LFOGroup
from jdxi_editor.ui.editors.base.lfo.layout import LFOLayoutSpec
from jdxi_editor.ui.editors.base.lfo.widgets import LFOWidgets
from jdxi_editor.ui.editors.base.wave.spec import ModeButtonSpec
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.spec import SliderSpec, SwitchSpec


class BaseLFOSection(SectionBaseWidget):
    """Abstract base class for LFO sections. All LFOs (Analog, Digital, Mod) use _create_shape_row() for exclusive wave shape selection."""

    SKIP_BASE_SETUP_UI = True  # We build layout in _setup_ui() via _create_shape_row(), not base's tab layout

    SYNTH_SPEC: Digital | Analog = None

    rate_tab_label: str = "Rate"
    depths_tab_label: str = "Depths"

    def __init__(
        self,
        icons_row_type: str = IconType.ADSR,
        analog: bool = False,
        send_midi_parameter: Callable = None,
        address: JDXiSysExAddress = None,
        midi_helper: MidiIOHelper = None,
    ):
        """
        Initialize the BaseLFOSection

        :param icons_row_type: Type of icon e.g
        :param analog: bool
        :param send_midi_parameter: Callable to send MIDI parameter updates
        :param address: Optional RolandSysExAddress for partial/tone
        :param midi_helper: Optional MidiIOHelper for MIDI communication
        :param controls: Optional dict of parameter controls (from panel)
        """
        self.widgets: LFOWidgets | None = None
        self.wave_shape_param: list | None = None
        self.send_midi_parameter: Callable | None = send_midi_parameter
        super().__init__(
            send_midi_parameter=send_midi_parameter,
            midi_helper=midi_helper,
            address=address,
            icons_row_type=icons_row_type,
            analog=analog,
        )
        self.wave_shapes = self.generate_mode_button_specs()
        self.lfo_shape_buttons: dict[int, QPushButton] = {}
        if not hasattr(self, "controls") or self.controls is None:
            self.controls = {}
        # All LFOs (Digital, Mod, Analog) use this path so shape row comes from _create_shape_row() with QButtonGroup
        self._setup_ui()

    def generate_mode_button_specs(self) -> list:
        """generate_mode_button_specs, was generate_wave_shapes"""
        W: DigitalWave | AnalogWave = self.SYNTH_SPEC.Wave
        I = JDXi.UI.Icon
        wave_shapes = [
            ModeButtonSpec(shape=W.LFO.TRI, icon=I.Wave.Icon.TRIANGLE),
            ModeButtonSpec(shape=W.LFO.SINE, icon=I.Wave.Icon.SINE),
            ModeButtonSpec(shape=W.LFO.SAW, icon=I.Wave.Icon.SAW),
            ModeButtonSpec(shape=W.LFO.SQUARE, icon=I.Wave.Icon.SQUARE),
            ModeButtonSpec(shape=W.LFO.SAMPLE_HOLD, icon=I.Wave.Icon.WAVEFORM),
            ModeButtonSpec(shape=W.LFO.RANDOM, icon=I.Wave.Icon.RANDOM),
        ]
        return wave_shapes

    def _setup_ui(self):
        """Main construction pipeline"""
        # --- Restore wave_shapes/icon_map if SectionBaseWidget.__init__() overwrote them
        if self.wave_shapes is None:
            self.wave_shapes = self.generate_mode_button_specs()
        if self.wave_shape_buttons is None:
            self.wave_shape_buttons = {}

        # 1) build widgets
        self.widgets: LFOWidgets = self._build_widgets()

        # 2) root layout
        layout = self.create_layout()

        # 3) layout mode
        if self.analog:
            self._build_analog_layout(layout)
        else:
            self._build_digital_layout(layout)

        layout.addStretch()

    def build_widgets(self):
        """Build LFO widgets (switches, depth, rate). Shape row is created in _setup_ui() via _create_shape_row(), not _create_waveform_buttons()."""
        self._build_widgets()

    def _build_widgets(self) -> LFOWidgets:
        spec = self._build_layout_spec()

        return LFOWidgets(
            switches=self._build_switches(spec.switches),
            depth=self._build_sliders(spec.depth_sliders),
            rate=self._build_sliders(spec.rate_sliders),
        )

    def _build_analog_layout(self, layout):
        layout.addLayout(self._create_shape_row())
        rows = [self.widgets.switches, self.widgets.depth, self.widgets.rate]
        self._add_group_with_widget_rows(LFOGroup.label, rows)

    def _build_digital_layout(self, layout):
        layout.addLayout(self._create_shape_row())

        # switch row
        layout.addWidget(self._wrap_row(self.widgets.switches))

        # tabs
        tabs = QTabWidget()
        tabs.addTab(self._wrap_row(self.widgets.rate), self.rate_tab_label)
        tabs.addTab(self._wrap_row(self.widgets.depth), self.depths_tab_label)

        JDXi.UI.Theme.apply_tabs_style(tabs, analog=False)

        layout.addWidget(tabs)

    def _build_layout_spec(self):
        P = self.SYNTH_SPEC.Param
        D = self.SYNTH_SPEC.Display

        switches = [
            SwitchSpec(
                P.LFO_TEMPO_SYNC_SWITCH,
                D.Name.LFO_TEMPO_SYNC_SWITCH,
                D.Options.LFO_TEMPO_SYNC_SWITCH,
            ),
            SwitchSpec(
                P.LFO_TEMPO_SYNC_NOTE,
                D.Name.LFO_TEMPO_SYNC_NOTE,
                D.Options.LFO_TEMPO_SYNC_NOTE,
            ),
            SwitchSpec(
                P.LFO_KEY_TRIGGER, D.Name.LFO_KEY_TRIGGER, D.Options.LFO_KEY_TRIGGER
            ),
        ]

        depths = [
            SliderSpec(P.LFO_PITCH_DEPTH, D.Name.LFO_PITCH_DEPTH),
            SliderSpec(P.LFO_FILTER_DEPTH, D.Name.LFO_FILTER_DEPTH),
            SliderSpec(P.LFO_AMP_DEPTH, D.Name.LFO_AMP_DEPTH),
        ]

        if hasattr(P, "LFO_PAN_DEPTH"):
            depths.append(
                SliderSpec(P.LFO_PAN_DEPTH, getattr(D.Name, "LFO_PAN_DEPTH", "Pan"))
            )

        rate = [
            SliderSpec(P.LFO_RATE, D.Name.LFO_RATE),
            SliderSpec(P.LFO_FADE_TIME, D.Name.LFO_FADE_TIME),
        ]

        return LFOLayoutSpec(switches, depths, rate)
