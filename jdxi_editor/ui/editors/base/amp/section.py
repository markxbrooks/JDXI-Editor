"""
Base Amp Section 
"""

from dataclasses import dataclass
from typing import Callable, List, Optional

from PySide6.QtWidgets import QTabWidget, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import JDXiSysExAddress
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.adsr.parameters import ADSRParameters
from jdxi_editor.ui.editors.base.amp.widget import AmpWidgets
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import create_layout_with_widgets
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget


class BaseAmpSection(SectionBaseWidget):
    """Base Amp Section"""

    def __init__(
        self,
        analog: bool = False,
        send_midi_parameter: Callable = None,
        midi_helper: MidiIOHelper = None,
        address: JDXiSysExAddress = None,
    ):

        # Dynamic widgets storage
        self.AMP_PARAMETERS = {}
        self.amp_sliders = {}
        self.widgets: Optional[AmpWidgets] = None
        self.tab_widget = None
        self.layout = None

        super().__init__(
            icons_row_type=IconType.ADSR,
            analog=analog,
            midi_helper=midi_helper,
            send_midi_parameter=send_midi_parameter,
            address=address,
        )

    # ------------------------------------------------------------------
    # Build Widgets
    # ------------------------------------------------------------------
    def build_widgets(self):
        """Build all amp widgets from SLIDER_GROUPS['controls'] when present; Digital builds in _create_parameter_widgets override."""
        self.tab_widget = QTabWidget()
        JDXi.UI.Theme.apply_tabs_style(self.tab_widget, analog=self.analog)
        control_specs = self.spec.get("controls", []) if self.spec else []
        if control_specs:
            sliders = self._build_sliders(control_specs)
            for entry, slider in zip(control_specs, sliders):
                self.amp_sliders[entry.param] = slider
                self.controls[entry.param] = slider
        self._create_adsr_group()

    # ------------------------------------------------------------------
    # Setup UI
    # ------------------------------------------------------------------
    def setup_ui(self):
        """Setup the UI for the analog amp section"""
        self.layout = self.create_layout()

        # --- Level Controls Tab
        self.controls_layout = create_layout_with_widgets(
            list(self.amp_sliders.values())
        )
        self.level_controls_widget = QWidget()
        self.level_controls_widget.setLayout(self.controls_layout)

        self._add_tab(
            key=self.SYNTH_SPEC.Amp.Tab.CONTROLS, widget=self.level_controls_widget
        )

        # --- ADSR Tab
        self._add_tab(key=self.SYNTH_SPEC.Amp.Tab.ADSR, widget=self.adsr_group)

        # --- Add tab widget to main layout
        self.layout.addWidget(self.tab_widget)
        self.layout.addStretch()

        self.widgets = AmpWidgets(
            tab_widget=self.tab_widget,
            level_controls_widget=self.level_controls_widget,
            controls=list(self.amp_sliders.values()),
            adsr_widget=getattr(self, "adsr_widget", None),
            pan=None,
        )

    def set_level(self, value: int) -> None:
        self._set_param(self.SYNTH_SPEC.Param.AMP_LEVEL, value)

    def set_velocity_sensitivity(self, value: int) -> None:
        self._set_param(self.SYNTH_SPEC.Param.AMP_VELOCITY, value)

    def set_adsr(self, attack=None, decay=None, sustain=None, release=None):
        mapping = {
            attack: self.SYNTH_SPEC.Param.AMP_ENV_ATTACK_TIME,
            decay: self.SYNTH_SPEC.Param.AMP_ENV_DECAY_TIME,
            sustain: self.SYNTH_SPEC.Param.AMP_ENV_SUSTAIN_LEVEL,
            release: self.SYNTH_SPEC.Param.AMP_ENV_RELEASE_TIME,
        }
        for value, param in mapping.items():
            if value is not None:
                self._set_param(param, value)

    def _write_param(self, param, value: int) -> None:
        widget = self.controls.get(param)
        if widget is None:
            raise RuntimeError(f"No control bound for {param}")

        if hasattr(widget, "setValue"):
            widget.setValue(value)
            return

        if hasattr(widget, "combo_box"):
            widget.combo_box.setCurrentIndex(value)
            return

        raise TypeError(f"Unsupported widget type for {param}")

    def _resolve_param(self, name: str):
        try:
            return self.AMP_PARAMETERS[name]
        except KeyError:
            raise KeyError(f"{name} is not a valid AMP parameter")

    def __getitem__(self, name: str) -> int:
        param = self._resolve_param(name)
        return self._read_param(param)

    def __setitem__(self, name: str, value: int) -> None:
        param = self._resolve_param(name)
        self._write_param(param, value)

    def _read_param(self, param) -> int:
        """read param"""
        widget = self.controls.get(param)
        if widget is None:
            raise RuntimeError(f"No control bound for {param}")

        if hasattr(widget, "value"):
            return widget.value()

        if hasattr(widget, "combo_box"):
            return widget.combo_box.currentIndex()

        raise TypeError(f"Unsupported widget type for {param}")

    def set_envelope(self, env: ADSRParameters):
        """set envelope"""
        self.set_adsr(env.attack, env.decay, env.sustain, env.release)

    def get_envelope(self) -> ADSRParameters:
        """get envelope"""
        return ADSRParameters(
            self._read_param(self.SYNTH_SPEC.Param.AMP_ENV_ATTACK_TIME),
            self._read_param(self.SYNTH_SPEC.Param.AMP_ENV_DECAY_TIME),
            self._read_param(self.SYNTH_SPEC.Param.AMP_ENV_SUSTAIN_LEVEL),
            self._read_param(self.SYNTH_SPEC.Param.AMP_ENV_RELEASE_TIME),
        )

    def _build_amp_parameters(self):
        """build adsr parameters"""
        return {
            "level": self.SYNTH_SPEC.Param.AMP_LEVEL,
            "velocity": self.SYNTH_SPEC.Param.AMP_VELOCITY,
            "keyfollow": self.SYNTH_SPEC.Param.AMP_LEVEL_KEYFOLLOW,
            "aftertouch": self.SYNTH_SPEC.Param.LEVEL_AFTERTOUCH,
            "cutoff_aftertouch": self.SYNTH_SPEC.Param.CUTOFF_AFTERTOUCH,
            "pan": self.SYNTH_SPEC.Param.AMP_PAN,
        }
