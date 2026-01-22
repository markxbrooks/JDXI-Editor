"""
Amp section of the JD-Xi editor

This section contains the controls for the amp section of the JD-Xi editor.
"""

from typing import Callable

from PySide6.QtWidgets import (
    QTabWidget,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.parameter.analog.address import AnalogParam
from jdxi_editor.midi.data.parameter.analog.name import AnalogDisplayName
from jdxi_editor.ui.widgets.adsr.adsr import ADSR
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import (
    create_adsr_icon,
    create_envelope_group,
    create_layout_with_widgets,
)
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget


class AnalogAmpSection(SectionBaseWidget):
    """Amp section of the JD-Xi editor"""

    AMP_LEVEL_PARAMS = [
        {"param": AnalogParam.AMP_LEVEL, "display": AnalogDisplayName.AMP_LEVEL},
        {"param": AnalogParam.AMP_LEVEL_KEYFOLLOW, "display": AnalogDisplayName.AMP_LEVEL_KEYFOLLOW},
        {"param": AnalogParam.AMP_LEVEL_VELOCITY_SENSITIVITY, "display": AnalogDisplayName.AMP_LEVEL_VELOCITY_SENSITIVITY},
    ]

    AMP_ADSR_PARAMS = {
        "attack": AnalogParam.AMP_ENV_ATTACK_TIME,
        "decay": AnalogParam.AMP_ENV_DECAY_TIME,
        "sustain": AnalogParam.AMP_ENV_SUSTAIN_LEVEL,
        "release": AnalogParam.AMP_ENV_RELEASE_TIME,
    }

    def __init__(
        self,
        midi_helper,
        address,
        controls: dict,
        create_parameter_slider: Callable,
    ):
        self.midi_helper = midi_helper
        self.address = address
        self.controls = controls
        self._create_parameter_slider = create_parameter_slider

        # Dynamic widgets storage
        self.amp_sliders = {}
        self.amp_adsr_group = None
        self.amp_env_adsr_widget = None
        self.analog_amp_tab_widget = None
        self.layout = None

        super().__init__(icon_type=IconType.ADSR, analog=True)

        self.build_widgets()
        self.setup_ui()

    # ------------------------------------------------------------------
    # Build Widgets
    # ------------------------------------------------------------------
    def build_widgets(self):
        """Build all amp widgets"""
        self.analog_amp_tab_widget = QTabWidget()
        self._create_amp_level_sliders()
        self._create_amp_adsr_group()

    def _create_amp_level_sliders(self):
        """Create sliders for Level, KeyFollow, and Velocity Sensitivity"""
        for entry in self.AMP_LEVEL_PARAMS:
            slider = self._create_parameter_slider(entry["param"], entry["display"], vertical=True)
            self.amp_sliders[entry["param"]] = slider
            self.controls[entry["param"]] = slider

    def _create_amp_adsr_group(self):
        """Create amp ADSR envelope using standardized helper"""
        self.amp_env_adsr_widget = ADSR(
            attack_param=self.AMP_ADSR_PARAMS["attack"],
            decay_param=self.AMP_ADSR_PARAMS["decay"],
            sustain_param=self.AMP_ADSR_PARAMS["sustain"],
            release_param=self.AMP_ADSR_PARAMS["release"],
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            address=self.address,
            controls=self.controls,
            analog=True,
        )
        self.amp_adsr_group = create_envelope_group(
            name="Envelope",
            adsr_widget=self.amp_env_adsr_widget,
            analog=True,
        )

    # ------------------------------------------------------------------
    # Setup UI
    # ------------------------------------------------------------------
    def setup_ui(self):
        """Setup the UI for the analog amp section"""
        self.layout = self.create_layout()

        # --- Level Controls Tab
        level_controls_layout = create_layout_with_widgets(list(self.amp_sliders.values()))
        level_controls_widget = QWidget()
        level_controls_widget.setLayout(level_controls_layout)

        controls_icon = JDXi.UI.IconRegistry.get_icon(
            JDXi.UI.IconRegistry.TUNE, color=JDXi.UI.Style.GREY
        )
        self.analog_amp_tab_widget.addTab(level_controls_widget, controls_icon, AnalogDisplayName.CONTROLS)

        # --- ADSR Tab
        adsr_icon = create_adsr_icon()
        self.analog_amp_tab_widget.addTab(self.amp_adsr_group, adsr_icon, AnalogDisplayName.ADSR)

        JDXi.UI.ThemeManager.apply_tabs_style(self.analog_amp_tab_widget, analog=True)

        # --- Add tab widget to main layout
        self.layout.addWidget(self.analog_amp_tab_widget)
        self.layout.addStretch()
