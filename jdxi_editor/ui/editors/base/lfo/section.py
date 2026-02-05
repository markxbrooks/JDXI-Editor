"""
LFO section of the digital partial editor.
"""
from typing import Callable

from PySide6.QtWidgets import QTabWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.ui.editors.base.lfo.group import LFOGroup
from jdxi_editor.ui.editors.base.lfo.layout import LFOLayoutSpec
from jdxi_editor.ui.editors.base.lfo.widgets import LFOWidgets
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.spec import SliderSpec, SwitchSpec


class BaseLFOSection(SectionBaseWidget):
    """Abstract base class for LFO sections."""

    SYNTH_SPEC: Digital | Analog = None

    rate_tab_label: str = "Rate"
    depths_tab_label: str = "Depths"

    def __init__(
        self,
        icons_row_type: str = IconType.ADSR,
        analog: bool = False,
        send_midi_parameter: Callable = None,
    ):
        """
        Initialize the DigitalLFOSection

        :param icons_row_type: Type of icon e.g
        :param analog: bool
        """
        self.widgets: LFOWidgets | None = None
        self.wave_shape_param: list | None = None
        self.send_midi_parameter: Callable | None = send_midi_parameter
        self.wave_shape_buttons = {}  # Dictionary to store LFO shape buttons

        super().__init__(
            icons_row_type=icons_row_type,
            analog=analog,
            send_midi_parameter=send_midi_parameter,
        )
        # --- Restore wave_shapes, icon map, and buttons after super().__init__() (SectionBaseWidget overwrites them)
        # Note: _setup_ui() may have already run during super().__init__(), so we restore here and _setup_ui() also checks
        self.wave_shapes = self.generate_wave_shapes()
        self.wave_shape_icon_map = self.generate_wave_icon_map()
        self.shape_icon_map = self.wave_shape_icon_map
        self.wave_shape_buttons = {}
        # --- Set controls after super().__init__() to avoid it being overwritten
        if not hasattr(self, "controls") or self.controls is None:
            self.controls = {}

    def generate_wave_icon_map(self):
        """generate wave icon map"""
        W = self.SYNTH_SPEC.Wave
        I = JDXi.UI.Icon
        shape_icon_map = {
            W.LFO.TRI: I.WAVE_TRIANGLE,
            W.LFO.SINE: I.WAVE_SINE,
            W.LFO.SAW: I.WAVE_SAW,
            W.LFO.SQUARE: I.WAVE_SQUARE,
            W.LFO.SAMPLE_HOLD: I.WAVEFORM,
            W.LFO.RANDOM: I.WAVE_RANDOM,
        }
        return shape_icon_map

    def generate_wave_shapes(self) -> list:
        """generate_wave_shapes"""
        W = self.SYNTH_SPEC.Wave
        wave_shapes = [
            W.LFO.TRI,
            W.LFO.SINE,
            W.LFO.SAW,
            W.LFO.SQUARE,
            W.LFO.SAMPLE_HOLD,
            W.LFO.RANDOM,
        ]
        return wave_shapes

    def _setup_ui(self):
        """Main construction pipeline"""
        # --- Restore wave_shapes/icon_map if SectionBaseWidget.__init__() overwrote them
        if self.wave_shapes is None:
            self.wave_shapes = self.generate_wave_shapes()
        if self.wave_shape_icon_map is None or not hasattr(self, "shape_icon_map") or self.shape_icon_map is None:
            self.wave_shape_icon_map = self.generate_wave_icon_map()
            self.shape_icon_map = self.wave_shape_icon_map
        if self.wave_shape_buttons is None:
            self.wave_shape_buttons = {}

        # 1) build widgets
        self.lfo: LFOWidgets = self._build_widgets()

        # 2) root layout
        layout = self.create_layout()

        # 3) layout mode
        if self.analog:
            self._build_analog_layout(layout)
        else:
            self._build_digital_layout(layout)

        layout.addStretch()

    def _build_widgets(self) -> LFOWidgets:
        spec = self._build_layout_spec()

        return LFOWidgets(
            switches=self._build_switches(spec.switches),
            depth=self._build_sliders(spec.depth_sliders),
            rate=self._build_sliders(spec.rate_sliders),
        )

    def _build_analog_layout(self, layout):
        layout.addLayout(self._create_shape_row())
        rows = [self.lfo.switches, self.lfo.depth, self.lfo.rate]
        self._add_group_with_widget_rows(LFOGroup.label, rows)

    def _build_digital_layout(self, layout):
        layout.addLayout(self._create_shape_row())

        # switch row
        layout.addWidget(self._wrap_row(self.lfo.switches))

        # tabs
        tabs = QTabWidget()
        tabs.addTab(self._wrap_row(self.lfo.rate), self.rate_tab_label)
        tabs.addTab(self._wrap_row(self.lfo.depth), self.depths_tab_label)

        JDXi.UI.Theme.apply_tabs_style(tabs, analog=False)

        layout.addWidget(tabs)

    def _build_layout_spec(self):
        P = self.SYNTH_SPEC.Param
        D = self.SYNTH_SPEC.Display

        switches = [
            SwitchSpec(P.LFO_TEMPO_SYNC_SWITCH, D.Name.LFO_TEMPO_SYNC_SWITCH, D.Options.LFO_TEMPO_SYNC_SWITCH),
            SwitchSpec(P.LFO_TEMPO_SYNC_NOTE, D.Name.LFO_TEMPO_SYNC_NOTE, D.Options.LFO_TEMPO_SYNC_NOTE),
            SwitchSpec(P.LFO_KEY_TRIGGER, D.Name.LFO_KEY_TRIGGER, D.Options.LFO_KEY_TRIGGER),
        ]

        depths = [
            SliderSpec(P.LFO_PITCH_DEPTH, D.Name.LFO_PITCH_DEPTH),
            SliderSpec(P.LFO_FILTER_DEPTH, D.Name.LFO_FILTER_DEPTH),
            SliderSpec(P.LFO_AMP_DEPTH, D.Name.LFO_AMP_DEPTH),
        ]

        if hasattr(P, "LFO_PAN_DEPTH"):
            depths.append(SliderSpec(P.LFO_PAN_DEPTH, getattr(D.Name, "LFO_PAN_DEPTH", "Pan")))

        rate = [
            SliderSpec(P.LFO_RATE, D.Name.LFO_RATE),
            SliderSpec(P.LFO_FADE_TIME, D.Name.LFO_FADE_TIME),
        ]

        return LFOLayoutSpec(switches, depths, rate)
