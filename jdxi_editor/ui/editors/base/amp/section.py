"""
Base Amp Section
"""

from dataclasses import dataclass
from typing import Callable, List, Optional

from picomidi.message.type import MidoMessageType
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

    # Skip SectionBaseWidget._setup_ui() so we don't add Controls/ADSR tabs twice:
    # base _setup_ui() calls _create_tab_widget() which adds them, then our setup_ui() adds them again.
    SKIP_BASE_SETUP_UI = True

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
    # Build Widgets (unified flow: both Analog and Digital)
    # ------------------------------------------------------------------
    def build_widgets(self):
        """Create tab widget, build control widgets (subclass hook), create ADSR. Subclasses override _build_control_widgets for their controls."""
        self.tab_widget = QTabWidget()
        JDXi.UI.Theme.apply_tabs_style(self.tab_widget, analog=self.analog)
        self._build_control_widgets()
        self._create_adsr_group()

    def _build_control_widgets(self):
        """Build control sliders from spec.controls into amp_sliders and self.controls. Digital overrides to populate amp_control_widgets (and pan) instead."""
        control_specs = getattr(self.spec, "controls", None) or [] if self.spec else []
        if control_specs:
            sliders = self._build_sliders(control_specs)
            for entry, slider in zip(control_specs, sliders):
                self.amp_sliders[entry.param] = slider
                self.controls[entry.param] = slider

    # ------------------------------------------------------------------
    # Setup UI (unified flow: both Analog and Digital)
    # ------------------------------------------------------------------
    def setup_ui(self):
        """Create layout, add Controls and ADSR tabs, add tab widget to layout, build widgets container. Subclasses override _create_controls_widget and _build_amp_widgets as needed."""
        self.layout = self.create_layout()
        self.level_controls_widget = self._create_controls_widget()
        self._add_tab(
            key=self.SYNTH_SPEC.Amp.Tab.CONTROLS, widget=self.level_controls_widget
        )
        self._add_tab(key=self.SYNTH_SPEC.Amp.Tab.ADSR, widget=self.adsr_group)
        self.layout.addWidget(self.tab_widget)
        self.layout.addStretch()
        self.widgets = self._build_amp_widgets()

    def _create_controls_widget(self) -> QWidget:
        """Build the Controls tab content. Base: vertical sliders from amp_sliders. Digital overrides to add amp_control_widgets + pan."""
        self.controls_layout = create_layout_with_widgets(
            list(self.amp_sliders.values())
        )
        level_controls_widget = QWidget()
        level_controls_widget.setLayout(self.controls_layout)
        return level_controls_widget

    def _build_amp_widgets(self) -> AmpWidgets:
        """Build the AmpWidgets container. Digital overrides to return DigitalAmpWidgets with pan."""
        return AmpWidgets(
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
