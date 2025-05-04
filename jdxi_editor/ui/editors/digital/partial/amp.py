"""
 AMP section for the digital partial editor.
"""

from typing import Callable
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox
from PySide6.QtCore import Qt
import qtawesome as qta

from jdxi_editor.midi.data.parameter.digital.partial import (
    AddressParameterDigitalPartial,
)
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.jdxi.style import JDXIStyle
from jdxi_editor.ui.widgets.adsr.adsr import ADSR


class DigitalAmpSection(QWidget):
    """Digital Amp Section for the JDXI Editor"""

    def __init__(
        self,
        create_parameter_slider: Callable,
        partial_number: int,
        midi_helper: MidiIOHelper,
        controls: dict,
        address: RolandSysExAddress,
    ):
        super().__init__()
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
        self.setup_ui()

    def setup_ui(self):
        """Setup the amplifier section UI."""
        amp_section_layout = QVBoxLayout()
        self.setLayout(amp_section_layout)

        # Icons layout
        icons_hlayout = QHBoxLayout()
        for icon in [
            "mdi.volume-variant-off",
            "mdi6.volume-minus",
            "mdi.amplifier",
            "mdi6.volume-plus",
            "mdi.waveform",
        ]:
            icon_label = QLabel()
            icon = qta.icon(icon, color="#666666")
            pixmap = icon.pixmap(JDXIStyle.ICON_SIZE, JDXIStyle.ICON_SIZE)
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            icons_hlayout.addWidget(icon_label)
        amp_section_layout.addLayout(icons_hlayout)

        # Level and velocity controls
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout()
        controls_group.setLayout(controls_layout)

        controls_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.AMP_LEVEL, "Level"
            )
        )
        controls_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.AMP_VELOCITY, "Velocity"
            )
        )
        # Create and center the pan slider
        pan_slider = self._create_parameter_slider(
            AddressParameterDigitalPartial.AMP_PAN, "Pan"
        )
        pan_slider.setValue(0)
        controls_layout.addWidget(pan_slider)
        amp_section_layout.addWidget(controls_group)

        # Amp envelope
        env_group = QGroupBox("Envelope")
        env_group.setProperty("adsr", True)
        env_layout = QHBoxLayout()
        amp_env_adsr_vlayout = QVBoxLayout()
        env_group.setLayout(amp_env_adsr_vlayout)

        # Generate the ADSR waveform icon
        icon_base64 = generate_waveform_icon("adsr", "#FFFFFF", 2.0)
        pixmap = base64_to_pixmap(icon_base64)

        icon_label = QLabel()
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        icons_hlayout = QHBoxLayout()
        icons_hlayout.addWidget(icon_label)
        amp_section_layout.addLayout(icons_hlayout)

        # Create ADSRWidget
        (
            group_address,
            _,
        ) = AddressParameterDigitalPartial.AMP_ENV_ATTACK_TIME.get_address_for_partial(
            self.partial_number
        )
        self.amp_env_adsr_widget = ADSR(
            attack_param=AddressParameterDigitalPartial.AMP_ENV_ATTACK_TIME,
            decay_param=AddressParameterDigitalPartial.AMP_ENV_DECAY_TIME,
            sustain_param=AddressParameterDigitalPartial.AMP_ENV_SUSTAIN_LEVEL,
            release_param=AddressParameterDigitalPartial.AMP_ENV_RELEASE_TIME,
            midi_helper=self.midi_helper,
            address=self.address,
        )
        self.amp_env_adsr_widget.setStyleSheet(JDXIStyle.ADSR)
        env_layout.addLayout(amp_env_adsr_vlayout)
        amp_env_adsr_vlayout.addWidget(self.amp_env_adsr_widget)
        amp_env_adsr_vlayout.setStretchFactor(self.amp_env_adsr_widget, 5)
        amp_env_adsr_vlayout.addLayout(env_layout)
        amp_section_layout.addWidget(env_group)
        amp_section_layout.addStretch()

        # Keyfollow and aftertouch
        controls_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.AMP_LEVEL_KEYFOLLOW, "KeyFollow"
            )
        )
        controls_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.LEVEL_AFTERTOUCH, "AT Sens"
            )
        )
