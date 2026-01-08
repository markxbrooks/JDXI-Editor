"""
AMP section for the digital partial editor.
"""

from typing import Callable

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.parameter.digital.partial import (
    DigitalPartialParam,
)
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.ui.widgets.adsr.adsr import ADSR
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions
from picomidi.sysex.parameter.address import AddressParameter


class DigitalAmpSection(QWidget):
    """Digital Amp Section for the JDXI Editor"""

    def __init__(
        self,
        create_parameter_slider: Callable,
        partial_number: int,
        midi_helper: MidiIOHelper,
        controls: dict[AddressParameter, QWidget],
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
        amp_section_layout.setContentsMargins(5, 15, 5, 5)
        amp_section_layout.setSpacing(5)
        self.setStyleSheet(JDXiStyle.ADSR)
        self.setMinimumHeight(JDXiDimensions.EDITOR_MINIMUM_HEIGHT)

        # Icons layout
        icons_hlayout = self._create_icons_layout()
        amp_section_layout.addLayout(icons_hlayout)

        # Create tab widget
        self.digital_amp_tab_widget = QTabWidget()
        amp_section_layout.addWidget(self.digital_amp_tab_widget)

        # Add Controls tab
        amp_controls_layout = self._create_amp_controls_layout()
        amp_controls_widget = QWidget()
        amp_controls_widget.setLayout(amp_controls_layout)
        self.digital_amp_tab_widget.addTab(amp_controls_widget, "Controls")

        # Add ADSR tab
        amp_adsr_group = self._create_amp_adsr_group()
        self.digital_amp_tab_widget.addTab(amp_adsr_group, "ADSR")

        amp_section_layout.addSpacing(10)
        amp_section_layout.addStretch()

    def _create_icons_layout(self) -> QHBoxLayout:
        """Create icons layout"""
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
        return icons_hlayout

    def _create_amp_controls_layout(self) -> QVBoxLayout:
        """Create amp controls layout"""
        main_layout = QVBoxLayout()

        # Level and velocity controls row
        controls_row_layout = QHBoxLayout()
        controls_row_layout.addStretch()

        controls_row_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParam.AMP_LEVEL, "Level", vertical=True
            )
        )
        controls_row_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParam.AMP_VELOCITY, "Velocity", vertical=True
            )
        )
        controls_row_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParam.AMP_LEVEL_KEYFOLLOW, "KeyFollow", vertical=True
            )
        )
        controls_row_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParam.LEVEL_AFTERTOUCH,
                "After-touch Sensitivity",
                vertical=True,
            )
        )
        controls_row_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParam.CUTOFF_AFTERTOUCH,
                "After-touch Cutoff",
                vertical=True,
            )
        )
        controls_row_layout.addStretch()
        main_layout.addLayout(controls_row_layout)

        # Pan slider in a separate row
        pan_row_layout = QHBoxLayout()
        pan_row_layout.addStretch()
        pan_slider = self._create_parameter_slider(DigitalPartialParam.AMP_PAN, "Pan")
        pan_slider.setValue(0)
        pan_row_layout.addWidget(pan_slider)
        pan_row_layout.addStretch()
        main_layout.addLayout(pan_row_layout)

        main_layout.addStretch()
        return main_layout

    def _create_amp_adsr_group(self) -> QGroupBox:
        """Create amp ADSR group"""
        env_group = QGroupBox("Envelope")
        env_group.setProperty("adsr", True)
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
        amp_env_adsr_vlayout.addLayout(icons_hlayout)

        # Create ADSRWidget
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
        self.amp_env_adsr_widget.setStyleSheet(JDXiStyle.ADSR)
        amp_env_adsr_vlayout.addWidget(self.amp_env_adsr_widget)
        return env_group
