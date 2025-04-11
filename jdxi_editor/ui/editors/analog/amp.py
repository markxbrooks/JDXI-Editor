from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox
from PySide6.QtCore import Qt
import qtawesome as qta

from jdxi_editor.midi.data.parameter.analog import AnalogParameter
from jdxi_editor.ui.style import JDXIStyle
from jdxi_editor.ui.widgets.adsr.adsr import ADSR


class AmpSection(QWidget):
    def __init__(self, midi_helper, area, part, group, create_parameter_slider, generate_waveform_icon, base64_to_pixmap):
        super().__init__()
        self.midi_helper = midi_helper
        self.address_msb = area
        self.address_umb = part
        self.address_lmb = group
        self._create_parameter_slider = create_parameter_slider
        self.generate_waveform_icon = generate_waveform_icon
        self.base64_to_pixmap = base64_to_pixmap
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(5, 15, 5, 5)
        self.setLayout(layout)

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
        layout.addLayout(icons_hlayout)

        # Level controls
        self.amp_level = self._create_parameter_slider(AnalogParameter.AMP_LEVEL,
                                                       "Level")
        self.amp_level_keyfollow = self._create_parameter_slider(AnalogParameter.AMP_LEVEL_KEYFOLLOW,
                                                                 "Keyfollow")
        layout.addWidget(self.amp_level)
        layout.addWidget(self.amp_level_keyfollow)

        # Add spacing
        layout.addSpacing(10)

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
            attack_param=AnalogParameter.AMP_ENV_ATTACK_TIME,
            decay_param=AnalogParameter.AMP_ENV_DECAY_TIME,
            sustain_param=AnalogParameter.AMP_ENV_SUSTAIN_LEVEL,
            release_param=AnalogParameter.AMP_ENV_RELEASE_TIME,
            midi_helper=self.midi_helper,
            area=self.address_msb,
            part=self.part,
            group=self.group
        )
        self.amp_env_adsr_widget.setStyleSheet(JDXIStyle.ADSR_ANALOG)
        amp_env_adsr_vlayout.addWidget(self.amp_env_adsr_widget)

        layout.addWidget(env_group)
        layout.addStretch()
