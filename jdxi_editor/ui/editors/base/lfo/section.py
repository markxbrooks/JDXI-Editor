"""
LFO section of the digital partial editor.
"""
from typing import Callable

from decologr import Decologr as log
from PySide6.QtWidgets import QLabel, QTabWidget, QWidget, QButtonGroup

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.ui.editors.base.lfo.group import LFOGroup
from jdxi_editor.ui.editors.base.lfo.layout import LFOLayoutSpec
from jdxi_editor.ui.editors.base.lfo.widgets import LFOWidgets
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import (
    create_button_with_icon,
    create_icon_from_qta,
    create_layout_with_widgets,
)
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
        # --- Set up LFO shapes and icon map before super().__init__() so _setup_ui() can use them
        self.wave_shapes = self.generate_wave_shapes()
        self.shape_icon_map = self.generate_wave_icon_map()

        super().__init__(
            icons_row_type=icons_row_type,
            analog=analog,
            send_midi_parameter=send_midi_parameter,
        )
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

    def _on_shape_group_changed(self, shape_value: int, checked: bool):
        if not checked:
            return
        shape = self.SYNTH_SPEC.LFO.Shape(shape_value)
        self.set_wave_shape(shape, send_midi=True)

    def set_wave_shape(self, shape, send_midi=False):
        """Update UI + optionally send MIDI"""

        btn = self.wave_shape_buttons.get(shape)
        if not btn:
            return

        # prevent recursive signals when updating from MIDI
        self.wave_shape_group.blockSignals(True)
        btn.setChecked(True)
        self.wave_shape_group.blockSignals(False)

        self._apply_wave_shape_style(shape)

        if send_midi and self.send_midi_parameter:
            if not self.send_midi_parameter(self.wave_shape_param, shape.value):
                log.warning(f"Failed to set Mod LFO shape to {shape.name}")

    def _apply_wave_shape_style(self, active_shape):
        for shape, btn in self.wave_shape_buttons.items():
            if shape == active_shape:
                if self.analog:
                    JDXi.UI.Theme.apply_button_analog_active(btn)
                else:
                    btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT_ACTIVE)
            else:
                if self.analog:
                    JDXi.UI.Theme.apply_button_rect_analog(btn)
                else:
                    btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)

    def _create_shape_row(self):
        """Shape and sync controls"""

        shape_label = QLabel("Shape")
        layout_widgets = [shape_label]

        self.wave_shape_group = QButtonGroup(self)
        self.wave_shape_group.setExclusive(True)

        for shape in self.wave_shapes:
            icon_name = self.shape_icon_map.get(shape, JDXi.UI.Icon.WAVEFORM)
            icon = create_icon_from_qta(icon_name)

            btn = create_button_with_icon(
                icon_name=shape.display_name,
                icon=icon,
                button_dimensions=JDXi.UI.Dimensions.WaveformIcon,
                icon_dimensions=JDXi.UI.Dimensions.LFOIcon,
            )

            btn.setCheckable(True)

            if self.analog:
                JDXi.UI.Theme.apply_button_rect_analog(btn)

            self.wave_shape_group.addButton(btn, shape.value)
            self.wave_shape_buttons[shape] = btn
            layout_widgets.append(btn)

        self.wave_shape_group.idToggled.connect(self._on_shape_group_changed)

        return create_layout_with_widgets(layout_widgets)

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

    def _wrap_row(self, widgets: list[QWidget]) -> QWidget:
        """
        Convert a list of controls into a QWidget row container.

        Qt rule: layouts cannot be inserted where a QWidget is required
        (tabs, group boxes, pages). So we wrap the layout inside a QWidget.
        """
        row_widget = QWidget()
        row_layout = create_layout_with_widgets(widgets)
        row_widget.setLayout(row_layout)
        return row_widget
