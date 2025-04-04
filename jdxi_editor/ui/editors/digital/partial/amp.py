"""
 AMP section for the digital partial editor.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox
from PySide6.QtCore import Qt
import qtawesome as qta

from jdxi_editor.midi.data.constants.digital import DIGITAL_SYNTH_1_AREA
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParameter
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.ui.style import Style
from jdxi_editor.ui.widgets.adsr.adsr import ADSR


class DigitalAmpSection(QWidget):
    """Digital Amp Section for the JDXI Editor"""

    def __init__(
        self,
        create_parameter_slider,
        partial_number,
        midi_helper,
        controls,
        part,
    ):
        super().__init__()
        self.partial_number = partial_number
        self.midi_helper = midi_helper
        self.part = part
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
            pixmap = icon.pixmap(Style.ICON_SIZE, Style.ICON_SIZE)
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            icons_hlayout.addWidget(icon_label)
        amp_section_layout.addLayout(icons_hlayout)

        # Level and velocity controls
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout()
        controls_group.setLayout(controls_layout)

        controls_layout.addWidget(
            self._create_parameter_slider(DigitalPartialParameter.AMP_LEVEL, "Level")
        )
        controls_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParameter.AMP_VELOCITY, "Velocity"
            )
        )
        # Create and center the pan slider
        pan_slider = self._create_parameter_slider(
            DigitalPartialParameter.AMP_PAN, "Pan"
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
        ) = DigitalPartialParameter.AMP_ENV_ATTACK_TIME.get_address_for_partial(
            self.partial_number
        )
        self.amp_env_adsr_widget = ADSR(
            attack_param=DigitalPartialParameter.AMP_ENV_ATTACK_TIME,
            decay_param=DigitalPartialParameter.AMP_ENV_DECAY_TIME,
            sustain_param=DigitalPartialParameter.AMP_ENV_SUSTAIN_LEVEL,
            release_param=DigitalPartialParameter.AMP_ENV_RELEASE_TIME,
            midi_helper=self.midi_helper,
            area=DIGITAL_SYNTH_1_AREA,
            part=self.part,
            group=group_address,
        )
        self.amp_env_adsr_widget.setStyleSheet(Style.JDXI_ADSR)
        env_layout.addLayout(amp_env_adsr_vlayout)
        amp_env_adsr_vlayout.addWidget(self.amp_env_adsr_widget)
        amp_env_adsr_vlayout.setStretchFactor(self.amp_env_adsr_widget, 5)
        amp_env_adsr_vlayout.addLayout(env_layout)
        amp_section_layout.addWidget(env_group)
        amp_section_layout.addStretch()

        # Keyfollow and aftertouch
        controls_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParameter.AMP_LEVEL_KEYFOLLOW, "KeyFollow"
            )
        )
        controls_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParameter.LEVEL_AFTERTOUCH, "AT Sens"
            )
        )
