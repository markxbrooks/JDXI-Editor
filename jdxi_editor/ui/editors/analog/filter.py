

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox
from PySide6.QtCore import Qt
import qtawesome as qta

from jdxi_editor.midi.data.parameter.analog import AnalogParameter
from jdxi_editor.ui.style import Style
from jdxi_editor.ui.widgets.adsr.adsr import ADSR


class AnalogFilterSection(QWidget):
    def __init__(self, create_parameter_slider,
                 create_parameter_switch,
                 on_filter_mode_changed,
                 send_control_change,
                 midi_helper,
                 area,
                 part,
                 group):
        super().__init__()
        self.filter_resonance = None
        self.create_parameter_slider = create_parameter_slider
        self.create_parameter_switch = create_parameter_switch
        self._on_filter_mode_changed = on_filter_mode_changed
        self.send_control_change = send_control_change
        self.midi_helper = midi_helper
        self.area = area
        self.part = part
        self.group = group
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # ADSR Icon Row
        adsr_icon_row_layout = QHBoxLayout()
        for icon in [
            "mdi.triangle-wave", "mdi.sine-wave", "fa5s.wave-square",
            "mdi.cosine-wave", "mdi.triangle-wave", "mdi.waveform"
        ]:
            adsr_icon_label = QLabel()
            icon_pixmap = qta.icon(icon, color="#666666").pixmap(30, 30)
            adsr_icon_label.setPixmap(icon_pixmap)
            adsr_icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            adsr_icon_row_layout.addWidget(adsr_icon_label)
        layout.addLayout(adsr_icon_row_layout)

        # Filter Controls
        self.filter_mode_switch = self.create_parameter_switch(AnalogParameter.FILTER_MODE_SWITCH,
                                                          "Filter",
                                                               ["BYPASS", "LPF"])
        self.filter_mode_switch.valueChanged.connect(lambda v: self._on_filter_mode_changed(v))
        self.filter_cutoff = self.create_parameter_slider(AnalogParameter.FILTER_CUTOFF,
                                                          "Cutoff")
        self.filter_resonance = self.create_parameter_slider(AnalogParameter.FILTER_RESONANCE,
                                                             "Resonance")
        self.filter_cutoff_keyfollow = self.create_parameter_slider(AnalogParameter.FILTER_CUTOFF_KEYFOLLOW,
                                                                    "Keyfollow")

        layout.addWidget(self.filter_mode_switch)
        layout.addWidget(self.filter_cutoff)
        layout.addWidget(self.filter_resonance)
        layout.addWidget(self.filter_cutoff_keyfollow)

        # Connect filter controls
        self.filter_resonance.valueChanged.connect(
            lambda v: self.send_control_change(
                AnalogParameter.FILTER_RESONANCE.value[0], v
            )
        )

        # Envelope Controls
        self.filter_env_depth = self.create_parameter_slider(AnalogParameter.FILTER_ENV_DEPTH, "Depth")
        self.filter_env_velocity_sens = self.create_parameter_slider(AnalogParameter.FILTER_ENV_VELOCITY_SENSITIVITY,
                                                                     "Env. Velocity Sens.")

        layout.addWidget(self.filter_env_depth)
        layout.addWidget(self.filter_env_velocity_sens)
        layout.addSpacing(10)

        # ADSR Widget
        self.filter_adsr_widget = ADSR(
            attack_param=AnalogParameter.FILTER_ENV_ATTACK_TIME,
            decay_param=AnalogParameter.FILTER_ENV_DECAY_TIME,
            sustain_param=AnalogParameter.FILTER_ENV_SUSTAIN_LEVEL,
            release_param=AnalogParameter.FILTER_ENV_RELEASE_TIME,
            midi_helper=self.midi_helper,
            area=self.area,
            part=self.part,
            group=self.group
        )
        self.filter_adsr_widget.setStyleSheet(Style.JDXI_ADSR_ANALOG)
        env_group = QGroupBox("Envelope")
        env_group.setProperty("adsr", True)
        env_layout = QHBoxLayout()
        env_layout.addWidget(self.filter_adsr_widget)
        env_group.setLayout(env_layout)
        layout.addWidget(env_group)

        layout.addStretch()
