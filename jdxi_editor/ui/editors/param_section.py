from typing import Callable

from PySide6.QtWidgets import QWidget, QTabWidget

from jdxi_editor.ui.editors.widget_specs import SliderSpec, SwitchSpec
from jdxi_editor.ui.widgets.editor import SectionBaseWidget, IconType
from jdxi_editor.ui.widgets.editor.helper import create_button_with_icon, create_layout_with_widgets


class ComboBoxSpec:
    pass


class ParameterSectionBase(SectionBaseWidget):
    """
    Generalized section for Digital/Analog editor.

    Handles:
      - Parameter sliders, switches, combos (from specs)
      - Optional ADSR/envelope
      - Optional waveform/mode buttons
      - Tabs (Controls / ADSR / Custom)
      - MIDI parameter sending
    """

    PARAM_SPECS: list = []  # list of SliderSpec / SwitchSpec / ComboBoxSpec
    ADSR_SPEC: dict | None = None  # optional envelope parameters
    BUTTON_SPECS: list = []  # optional waveform/mode/shape buttons
    BUTTON_ENABLE_RULES: dict = {}  # optional rules for enabling controls per button

    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_switch: Callable = None,
        create_parameter_combo_box: Callable = None,
        send_midi_parameter: Callable = None,
        midi_helper=None,
        controls: dict = None,
        address=None,
        icon_type: str = IconType.NONE,
        analog: bool = False,
    ):
        self.midi_helper = midi_helper
        self.controls = controls or {}
        self.address = address
        self.send_midi_parameter = send_midi_parameter

        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self._create_parameter_combo_box = create_parameter_combo_box

        self.tab_widget = None
        self.adsr_widget = None
        self.control_widgets = []
        self.button_widgets = {}

        super().__init__(icon_type=icon_type, analog=analog)

        self.build_widgets()
        self.setup_ui()
        if self.BUTTON_SPECS:
            self._initialize_button_states()

    # -------------------------------
    # Build Widgets
    # -------------------------------
    def build_widgets(self):
        """Build sliders, switches, combo boxes, buttons, and ADSR"""
        self._create_parameter_widgets()
        if self.BUTTON_SPECS:
            self._create_buttons()
        if self.ADSR_SPEC:
            self._create_adsr()

    def _create_parameter_widgets(self):
        """Create widgets from PARAM_SPECS declaratively"""
        for spec in self.PARAM_SPECS:
            if isinstance(spec, SliderSpec):
                widget = self._create_parameter_slider(spec.param, spec.label, vertical=True)
            elif isinstance(spec, SwitchSpec):
                widget = self._create_parameter_switch(spec.param, spec.label, spec.options)
            elif isinstance(spec, ComboBoxSpec):
                widget = self._create_parameter_combo_box(spec.param, spec.label, options=spec.options)
            else:
                continue
            self.controls[spec.param] = widget
            self.control_widgets.append(widget)

    def _create_buttons(self):
        """Create mode/waveform/shape buttons from BUTTON_SPECS"""
        for spec in self.BUTTON_SPECS:
            btn = create_button_with_icon(spec.icon_name, spec.icon)
            btn.clicked.connect(lambda _, b=spec.param: self._on_button_selected(b))
            self.button_widgets[spec.param] = btn
            self.controls[spec.param] = btn

    def _create_adsr(self):
        """Create ADSR widget from ADSR_SPEC"""
        self.adsr_widget = ADSR(
            attack_param=self.ADSR_SPEC["attack"],
            decay_param=self.ADSR_SPEC["decay"],
            sustain_param=self.ADSR_SPEC["sustain"],
            release_param=self.ADSR_SPEC["release"],
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            address=self.address,
            analog=self.analog,
        )

    # -------------------------------
    # Layout & Tabs
    # -------------------------------
    def setup_ui(self):
        """Assemble section UI"""
        layout = self.create_layout()
        if self.button_widgets:
            layout.addLayout(self._create_button_row_layout())
        self._create_tab_widget()
        layout.addWidget(self.tab_widget)
        layout.addStretch()

    def _create_tab_widget(self):
        """Create tab widget with controls and optional ADSR"""
        self.tab_widget = QTabWidget()

        # Controls tab
        controls_widget = QWidget()
        controls_layout = create_layout_with_widgets(self.control_widgets)
        controls_widget.setLayout(controls_layout)
        self.tab_widget.addTab(controls_widget, JDXi.UI.IconRegistry.get_icon(JDXi.UI.IconRegistry.TUNE, JDXi.UI.Style.GREY), "Controls")

        # ADSR tab
        if self.adsr_widget:
            adsr_group = create_envelope_group("Envelope", self.adsr_widget, analog=self.analog)
            self.tab_widget.addTab(adsr_group, create_adsr_icon(), "ADSR")

    # -------------------------------
    # Button Logic
    # -------------------------------
    def _on_button_selected(self, button_param):
        """Handle button selection & enabling dependent widgets"""
        for btn in self.button_widgets.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)
        selected_btn = self.button_widgets[button_param]
        selected_btn.setChecked(True)
        selected_btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT_ACTIVE)
        self._update_button_enabled_states(button_param)
        if self.send_midi_parameter:
            self.send_midi_parameter(button_param, selected_btn.value)

    def _update_button_enabled_states(self, button_param):
        """Enable/disable controls based on BUTTON_ENABLE_RULES"""
        # Disable all first
        for attrs in self.BUTTON_ENABLE_RULES.values():
            for attr in attrs:
                getattr(self, attr, None).setEnabled(False)
        # Enable per selected button
        for attr in self.BUTTON_ENABLE_RULES.get(button_param, []):
            getattr(self, attr, None).setEnabled(True)

    def _initialize_button_states(self):
        """Set initial button state (first in BUTTON_SPECS)"""
        if self.BUTTON_SPECS:
            first_param = self.BUTTON_SPECS[0].param
            self._on_button_selected(first_param)

    def _create_button_row_layout(self):
        pass
