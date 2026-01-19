"""
AMP section for the digital partial editor.
"""

from typing import Callable

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QGroupBox,
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
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
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
        )  # Use NONE since we have custom icons
        self.setup_ui()

    def setup_ui(self):
        """Setup the amplifier section UI."""
        amp_section_layout = self.get_layout(margins=(5, 15, 5, 5), spacing=5)
        self.setMinimumHeight(JDXi.UI.Dimensions.EDITOR.MINIMUM_HEIGHT)

        # Custom icons layout (kept for Digital Amp's unique icon set)
        icons_hlayout = create_icons_layout()
        amp_section_layout.addLayout(icons_hlayout)

        # Create tab widget
        self.digital_amp_tab_widget = QTabWidget()
        amp_section_layout.addWidget(self.digital_amp_tab_widget)

        # Add Controls tab
        amp_controls_layout = self._create_amp_controls_layout()
        amp_controls_widget = QWidget()
        amp_controls_widget.setLayout(amp_controls_layout)
        controls_icon = JDXi.UI.IconRegistry.get_icon(
            JDXi.UI.IconRegistry.TUNE, color=JDXi.UI.Style.GREY
        )
        self.digital_amp_tab_widget.addTab(
            amp_controls_widget, controls_icon, "Controls"
        )

        # Add ADSR tab
        amp_adsr_group = self._create_amp_adsr_group()
        adsr_icon_base64 = generate_waveform_icon("adsr", "#FFFFFF", 1.0)
        adsr_icon = QIcon(base64_to_pixmap(adsr_icon_base64))
        self.digital_amp_tab_widget.addTab(amp_adsr_group, adsr_icon, "ADSR")

        amp_section_layout.addSpacing(JDXi.UI.Dimensions.EDITOR_DIGITAL.SPACING)
        amp_section_layout.addStretch()

    def _create_amp_controls_layout(self) -> QVBoxLayout:
        """Create amp controls layout"""

        # --- Level and velocity controls row - standardized order: Level, KeyFollow, Velocity
        controls_row_layout = create_layout_with_widgets(
            [
                self._create_parameter_slider(
                    DigitalPartialParam.AMP_LEVEL,
                    DigitalDisplayName.AMP_LEVEL,
                    vertical=True,
                ),
                self._create_parameter_slider(
                    DigitalPartialParam.AMP_LEVEL_KEYFOLLOW,
                    DigitalDisplayName.AMP_LEVEL_KEYFOLLOW,
                    vertical=True,
                ),
                self._create_parameter_slider(
                    DigitalPartialParam.AMP_VELOCITY,
                    DigitalDisplayName.AMP_VELOCITY,
                    vertical=True,
                ),
                self._create_parameter_slider(
                    DigitalPartialParam.LEVEL_AFTERTOUCH,
                    DigitalDisplayName.LEVEL_AFTERTOUCH,
                    vertical=True,
                ),
                self._create_parameter_slider(
                    DigitalPartialParam.CUTOFF_AFTERTOUCH,
                    DigitalDisplayName.CUTOFF_AFTERTOUCH,
                    vertical=True,
                ),
            ]
        )

        # --- Pan slider in a separate row to get left to right
        pan_slider = self._create_parameter_slider(
            DigitalPartialParam.AMP_PAN, DigitalDisplayName.AMP_PAN
        )
        pan_slider.setValue(0)
        pan_row_layout = create_layout_with_widgets([pan_slider])

        # --- Create main layout with list of layouts
        main_layout = create_layout_with_inner_layouts(
            [controls_row_layout, pan_row_layout]
        )
        return main_layout

    def _create_amp_adsr_group(self) -> QGroupBox:
        """Create amp ADSR group (harmonized with Analog Amp, uses standardized helper)"""
        # --- Create ADSRWidget
        (
            group_address,
            _,
        ) = DigitalPartialParam.AMP_ENV_ATTACK_TIME.get_address_for_partial(
            self.partial_number
        )
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
        # Use standardized envelope group helper (centers icon automatically)
        return create_envelope_group(
            name="Envelope", adsr_widget=self.amp_env_adsr_widget, analog=False
        )
