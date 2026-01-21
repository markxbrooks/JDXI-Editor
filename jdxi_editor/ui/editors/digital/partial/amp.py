"""
AMP section for the digital partial editor.
"""

from typing import Callable

from PySide6.QtWidgets import (
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.parameter.digital.name import DigitalDisplayName
from jdxi_editor.midi.data.parameter.digital.partial import (
    DigitalPartialParam,
)
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.widget_specs import SliderSpec
from jdxi_editor.ui.widgets.adsr.adsr import ADSR
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import (
    create_envelope_group,
    create_icons_layout,
    create_layout_with_inner_layouts,
    create_layout_with_widgets,
)
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from picomidi.sysex.parameter.address import AddressParameter


class DigitalAmpSection(SectionBaseWidget):
    """Digital Amp Section for the JDXI Editor"""

    AMP_SLIDER_SPECS = [
        SliderSpec(DigitalPartialParam.AMP_LEVEL, DigitalDisplayName.AMP_LEVEL),
        SliderSpec(
            DigitalPartialParam.AMP_LEVEL_KEYFOLLOW,
            DigitalDisplayName.AMP_LEVEL_KEYFOLLOW,
        ),
        SliderSpec(DigitalPartialParam.AMP_VELOCITY, DigitalDisplayName.AMP_VELOCITY),
        SliderSpec(
            DigitalPartialParam.LEVEL_AFTERTOUCH, DigitalDisplayName.LEVEL_AFTERTOUCH
        ),
        SliderSpec(
            DigitalPartialParam.CUTOFF_AFTERTOUCH, DigitalDisplayName.CUTOFF_AFTERTOUCH
        ),
    ]

    def __init__(
        self,
        create_parameter_slider: Callable,
        partial_number: int,
        midi_helper: MidiIOHelper,
        controls: dict[AddressParameter, QWidget],
        address: RolandSysExAddress,
    ):
        """
        Initialize the DigitalAmpSection

        :param create_parameter_slider: Callable
        :param partial_number: int
        :param midi_helper: MidiIOHelper
        :param controls: dict
        :param address: RolandSysExAddress
        """
        self.partial_number = partial_number
        self.midi_helper = midi_helper
        self.address = address
        self.controls = controls
        self._create_parameter_slider = create_parameter_slider

        super().__init__(
            icon_type=IconType.NONE, analog=False
        )  # --- Use NONE since we have custom icons
        self.build_widgets()
        self.setup_ui()

    def build_widgets(self):
        """
        Instantiate all child widgets.

        Must be called before setup_ui(), as setup_ui()
        assumes widgets already exist.
        """
        self._create_amp_control_widgets()
        self._create_adsr_widget()
        self._create_controls_widget()  # Must be before _create_tab_widget()
        self._create_amp_adsr_group()  # Must be before _create_tab_widget()
        self._create_tab_widget()  # Must be last as it uses controls_widget and amp_adsr_group

    def setup_ui(self):
        """Setup the amplifier section UI."""
        layout = self.get_layout(margins=(5, 15, 5, 5), spacing=5)
        self.setMinimumHeight(JDXi.UI.Dimensions.EDITOR.MINIMUM_HEIGHT)
        # --- Custom icons layout (kept for Digital Amp's unique icon set)
        icons_hlayout = create_icons_layout()
        layout.addLayout(icons_hlayout)
        layout.addWidget(self.tab_widget)
        layout.addSpacing(JDXi.UI.Dimensions.EDITOR_DIGITAL.SPACING)
        layout.addStretch()

    def _create_tab_widget(self):
        """Create tab widget"""
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.controls_widget, self.controls_icon, "Controls")
        # --- Add ADSR tab
        self.tab_widget.addTab(
            self.amp_adsr_group, JDXi.UI.IconRegistry.get_generated_icon("adsr"), "ADSR"
        )

    def _create_controls_widget(self) -> None:
        """Add Controls tab"""
        controls_layout = self._create_controls_layout()
        self.controls_widget = QWidget()
        self.controls_widget.setLayout(controls_layout)
        self.controls_icon = JDXi.UI.IconRegistry.get_icon(
            JDXi.UI.IconRegistry.TUNE, color=JDXi.UI.Style.GREY
        )

    def _create_amp_adsr_group(self) -> None:
        """Create amp ADSR group (harmonized with Analog Amp, uses standardized helper)"""
        # --- Use standardized envelope group helper (centers icon automatically)
        self.amp_adsr_group = create_envelope_group(
            name="Envelope", adsr_widget=self.amp_env_adsr_widget, analog=False
        )

    def _create_controls_layout(self) -> QVBoxLayout:
        """Create amp controls layout"""
        # --- Level and velocity controls row - standardized order: Level, KeyFollow, Velocity
        controls_row_layout = create_layout_with_widgets(self.amp_control_widgets)
        self._create_horizontal_pan_slider()
        self.pan_slider.setValue(0)
        pan_row_layout = create_layout_with_widgets([self.pan_slider])
        # --- Create main layout with list of layouts
        main_layout = create_layout_with_inner_layouts(
            [controls_row_layout, pan_row_layout]
        )
        return main_layout

    def _create_adsr_widget(self):
        """Create ADSRWidget"""
        self.amp_env_adsr_widget = ADSR(
            attack_param=DigitalPartialParam.AMP_ENV_ATTACK_TIME,
            decay_param=DigitalPartialParam.AMP_ENV_DECAY_TIME,
            sustain_param=DigitalPartialParam.AMP_ENV_SUSTAIN_LEVEL,
            release_param=DigitalPartialParam.AMP_ENV_RELEASE_TIME,
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            address=self.address,
        )

    def _create_horizontal_pan_slider(self):
        """Create pan slider (horizontal, centered)."""
        self.pan_slider = self._create_parameter_slider(
            DigitalPartialParam.AMP_PAN,
            DigitalDisplayName.AMP_PAN,
        )
        self.pan_slider.setValue(0)

    def _create_amp_control_widgets(self):
        """Create amp control sliders."""
        self.amp_control_widgets = self._build_sliders(self.AMP_SLIDER_SPECS)
