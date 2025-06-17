"""
Amp section of the JD-Xi editor

This section contains the controls for the amp section of the JD-Xi editor.
"""

from typing import Callable

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox
from PySide6.QtCore import Qt
import qtawesome as qta

from jdxi_editor.midi.data.parameter import AddressParameter
from jdxi_editor.midi.data.parameter.analog import AddressParameterAnalog
from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.ui.widgets.adsr.adsr import ADSR
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.data.address.address import RolandSysExAddress


class AmpSection(QWidget):
    """Amp section of the JD-Xi editor"""

    def __init__(
        self,
        midi_helper: MidiIOHelper,
        address: RolandSysExAddress,
        controls: dict[AddressParameter, QWidget],
        create_parameter_slider: Callable,
        generate_waveform_icon: Callable,
        base64_to_pixmap: Callable,
    ):
        super().__init__()
        """
        Initialize the Amp section of the JD-Xi editor

        :param midi_helper: MidiIOHelper
        :param address: RolandSysExAddress
        :param create_parameter_slider: Callable
        :param generate_waveform_icon: Callable
        :param base64_to_pixmap: Callable
        """
        self.midi_helper = midi_helper
        self.address = address
        self.controls = controls
        self._create_parameter_slider = create_parameter_slider
        self.generate_waveform_icon = generate_waveform_icon
        self.base64_to_pixmap = base64_to_pixmap
        self.init_ui()

    def init_ui(self):
        """ Initialize UI """
        main_rows_vlayout = QVBoxLayout()
        main_rows_vlayout.setSpacing(5)
        main_rows_vlayout.setContentsMargins(5, 15, 5, 5)
        self.setLayout(main_rows_vlayout)
        self.setStyleSheet(JDXiStyle.ADSR_ANALOG)

        # Icon row
        icons_hlayout = QHBoxLayout()
        for icon in [
            "mdi.volume-variant-off",
            "mdi6.volume-minus",
            "mdi.amplifier",
            "mdi6.volume-plus",
            "mdi.waveform",
        ]:
            icon_label = QLabel()
            icon_pixmap = qta.icon(icon, color="#666666").pixmap(30, 30)
            icon_label.setPixmap(icon_pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            icons_hlayout.addWidget(icon_label)
        main_rows_vlayout.addLayout(icons_hlayout)

        # Level controls
        level_controls_row_layout = QHBoxLayout()
        main_rows_vlayout.addLayout(level_controls_row_layout)

        self.amp_level = self._create_parameter_slider(
            AddressParameterAnalog.AMP_LEVEL, "Level", vertical=True
        )
        self.amp_level_keyfollow = self._create_parameter_slider(
            AddressParameterAnalog.AMP_LEVEL_KEYFOLLOW, "Keyfollow", vertical=True
        )
        self.amp_level_velocity_sensitivity = self._create_parameter_slider(
            AddressParameterAnalog.AMP_LEVEL_VELOCITY_SENSITIVITY,
            "Velocity Sensitivity", vertical=True
        )

        level_controls_row_layout.addStretch()
        level_controls_row_layout.addWidget(self.amp_level)
        level_controls_row_layout.addWidget(self.amp_level_keyfollow)
        level_controls_row_layout.addWidget(self.amp_level_velocity_sensitivity)
        level_controls_row_layout.addStretch()
        # Add spacing
        main_rows_vlayout.addSpacing(10)

        # Amp Envelope
        env_group = QGroupBox("Envelope")
        env_group.setProperty("adsr", True)
        amp_env_adsr_vlayout = QVBoxLayout()
        env_group.setLayout(amp_env_adsr_vlayout)

        # ADSR Icon
        icon_base64 = self.generate_waveform_icon("adsr", "#FFFFFF", 2.0)
        pixmap = self.base64_to_pixmap(icon_base64)
        icon_label = QLabel()
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        icons_hlayout = QHBoxLayout()
        icons_hlayout.addWidget(icon_label)
        amp_env_adsr_vlayout.addLayout(icons_hlayout)

        # ADSR Widget
        self.amp_env_adsr_widget = ADSR(
            attack_param=AddressParameterAnalog.AMP_ENV_ATTACK_TIME,
            decay_param=AddressParameterAnalog.AMP_ENV_DECAY_TIME,
            sustain_param=AddressParameterAnalog.AMP_ENV_SUSTAIN_LEVEL,
            release_param=AddressParameterAnalog.AMP_ENV_RELEASE_TIME,
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            address=self.address,
            controls=self.controls
        )
        self.amp_env_adsr_widget.setStyleSheet(JDXiStyle.ADSR_ANALOG)
        amp_env_adsr_vlayout.addWidget(self.amp_env_adsr_widget)

        main_rows_vlayout.addWidget(env_group)
        main_rows_vlayout.addStretch()
