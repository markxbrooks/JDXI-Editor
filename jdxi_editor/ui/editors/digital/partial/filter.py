"""
Digital Filter Section for the JDXI Editor
"""

from typing import Callable

from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
)

from decologr import Decologr as log
from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.digital.filter import DigitalFilterMode
from jdxi_editor.midi.data.parameter.digital.name import DigitalDisplayName
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParam
from jdxi_editor.ui.widgets.adsr.adsr import ADSR
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import (
    create_adsr_icon,
    create_envelope_group,
    create_filter_button,
    create_group,
    create_layout_with_widgets,
)
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.filter.filter import FilterWidget


class DigitalFilterSection(SectionBaseWidget):
    """Refactored Filter section for the digital partial editor."""

    FILTER_MODES = [
        {"mode": DigitalFilterMode.BYPASS, "icon": "BYPASS_FILTER"},
        {"mode": DigitalFilterMode.LPF, "icon": "LPF_FILTER"},
        {"mode": DigitalFilterMode.HPF, "icon": "HPF_FILTER"},
        {"mode": DigitalFilterMode.BPF, "icon": "BPF_FILTER"},
        {"mode": DigitalFilterMode.PKG, "icon": "LPF_FILTER"},
        {"mode": DigitalFilterMode.LPF2, "icon": "LPF_FILTER"},
        {"mode": DigitalFilterMode.LPF3, "icon": "LPF_FILTER"},
        {"mode": DigitalFilterMode.LPF4, "icon": "LPF_FILTER"},
    ]

    FILTER_CONTROL_PARAMS = [
        DigitalPartialParam.FILTER_CUTOFF,
        DigitalPartialParam.FILTER_RESONANCE,
        DigitalPartialParam.FILTER_CUTOFF_KEYFOLLOW,
        DigitalPartialParam.FILTER_ENV_VELOCITY_SENSITIVITY,
        DigitalPartialParam.FILTER_ENV_DEPTH,
        DigitalPartialParam.FILTER_SLOPE,
    ]

    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_switch: Callable,
        partial_number: int,
        midi_helper,
        controls: dict,
        address,
        send_midi_parameter: Callable = None,
    ):
        self.partial_number = partial_number
        self.midi_helper = midi_helper
        self.controls = controls
        self.address = address
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self.send_midi_parameter = send_midi_parameter
        self.filter_mode_buttons = {}

        super().__init__(icon_type=IconType.ADSR, analog=False)
        self.setup_ui()
        log.parameter("initialization complete for", self)

    def setup_ui(self):
        """Set up the UI for the filter section."""
        self.setMinimumHeight(JDXi.UI.Dimensions.EDITOR.MINIMUM_HEIGHT)

        # --- Create filter mode row
        filter_mode_row = self._create_filter_controls_row()

        # --- Create tab widget
        self.digital_filter_tab_widget = QTabWidget()
        self.digital_filter_tab_widget.addTab(
            self._create_filter_controls_group(),
            JDXi.UI.IconRegistry.get_icon(
                JDXi.UI.IconRegistry.TUNE, color=JDXi.UI.Style.GREY
            ),
            "Controls",
        )
        self.digital_filter_tab_widget.addTab(
            self._create_filter_adsr_env_group(), create_adsr_icon(), "ADSR"
        )

        # --- Layout everything
        self.main_rows_layout = self.create_main_rows_layout()
        self.main_rows_layout.addLayout(filter_mode_row)
        self.main_rows_layout.addWidget(self.digital_filter_tab_widget)
        self.main_rows_layout.addStretch()

    # ------------------------------------------------------------------
    # Filter Mode Buttons
    # ------------------------------------------------------------------
    def _create_filter_controls_row(self) -> QHBoxLayout:
        """Create filter mode buttons row."""
        widgets = [QLabel("Mode")]
        for fm in self.FILTER_MODES:
            btn = self._create_filter_mode_button(fm["mode"], fm["icon"])
            self.filter_mode_buttons[fm["mode"]] = btn
            widgets.append(btn)
        return create_layout_with_widgets(widgets, vertical=False)

    def _create_filter_mode_button(
        self, mode: DigitalFilterMode, icon_type: str
    ) -> QPushButton:
        """Helper to create a single filter mode button."""
        btn = create_filter_button(icon_type, mode)
        btn.clicked.connect(lambda checked, m=mode: self._on_filter_mode_selected(m))
        return btn

    def _on_filter_mode_selected(self, filter_mode: DigitalFilterMode):
        """Handle filter mode button click."""
        # --- Reset all buttons
        for btn in self.filter_mode_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)

        # --- Activate selected
        selected_btn = self.filter_mode_buttons.get(filter_mode)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT_ACTIVE)

        self.update_controls_state(filter_mode.value)

        # --- Send MIDI
        if self.send_midi_parameter:
            if not self.send_midi_parameter(
                DigitalPartialParam.FILTER_MODE_SWITCH, filter_mode.value
            ):
                log.warning(f"Failed to set filter mode to {filter_mode.name}")

    # ------------------------------------------------------------------
    # Controls and ADSR Groups
    # ------------------------------------------------------------------
    def _create_filter_controls_group(self) -> QGroupBox:
        """Create the filter controls group."""
        self.filter_widget = FilterWidget(
            cutoff_param=DigitalPartialParam.FILTER_CUTOFF,
            slope_param=DigitalPartialParam.FILTER_SLOPE,
            create_parameter_slider=self._create_parameter_slider,
            create_parameter_switch=self._create_parameter_switch,
            midi_helper=self.midi_helper,
            parent=self,
            controls=self.controls,
            address=self.address,
        )

        control_widgets = [
            self.filter_widget,
            self._create_parameter_slider(
                DigitalPartialParam.FILTER_RESONANCE,
                DigitalDisplayName.FILTER_RESONANCE,
                vertical=True,
            ),
            self._create_parameter_slider(
                DigitalPartialParam.FILTER_CUTOFF_KEYFOLLOW,
                DigitalDisplayName.FILTER_CUTOFF_KEYFOLLOW,
                vertical=True,
            ),
            self._create_parameter_slider(
                DigitalPartialParam.FILTER_ENV_VELOCITY_SENSITIVITY,
                DigitalDisplayName.FILTER_ENV_VELOCITY_SENSITIVITY,
                vertical=True,
            ),
        ]
        controls_layout = create_layout_with_widgets(control_widgets)
        return create_group("Controls", controls_layout)

    def _create_filter_adsr_env_group(self) -> QGroupBox:
        """Create ADSR envelope group for the filter."""
        self.filter_adsr_widget = ADSR(
            attack_param=DigitalPartialParam.FILTER_ENV_ATTACK_TIME,
            decay_param=DigitalPartialParam.FILTER_ENV_DECAY_TIME,
            sustain_param=DigitalPartialParam.FILTER_ENV_SUSTAIN_LEVEL,
            release_param=DigitalPartialParam.FILTER_ENV_RELEASE_TIME,
            peak_param=DigitalPartialParam.FILTER_ENV_DEPTH,
            create_parameter_slider=self._create_parameter_slider,
            midi_helper=self.midi_helper,
            controls=self.controls,
            address=self.address,
        )
        return create_envelope_group(
            "Envelope", adsr_widget=self.filter_adsr_widget, analog=False
        )

    # ------------------------------------------------------------------
    # Enable/Disable Controls
    # ------------------------------------------------------------------
    def update_controls_state(self, mode: int):
        """Enable or disable controls based on filter mode."""
        enabled = mode != 0  # BYPASS disables everything
        for param in self.FILTER_CONTROL_PARAMS:
            if param in self.controls:
                self.controls[param].setEnabled(enabled)
        if self.filter_adsr_widget:
            self.filter_adsr_widget.setEnabled(enabled)
        if self.filter_widget:
            self.filter_widget.setEnabled(enabled)
            if hasattr(self.filter_widget, "plot"):
                filter_mode_str = "bypass" if mode == 0 else "lpf"
                self.filter_widget.filter_mode = filter_mode_str
                self.filter_widget.plot.set_filter_mode(filter_mode_str)
