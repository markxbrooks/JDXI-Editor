"""
    Digital Tone Modify Section
"""

from typing import Callable
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from jdxi_editor.midi.data.lfo.lfo import LFOSyncNote
from jdxi_editor.midi.data.parameter.digital.modify import AddressParameterDigitalModify


class DigitalToneModifySection(QWidget):
    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_combo_box: Callable,
        create_parameter_switch: Callable,
        controls: dict,
    ):
        """
        Initialize the DigitalToneModifySection

        :param create_parameter_slider: Callable
        :param create_parameter_combo_box: Callable
        :param create_parameter_switch: Callable
        :param controls: dict
        """
        super().__init__()
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_combo_box = create_parameter_combo_box
        self._create_parameter_switch = create_parameter_switch
        self.controls = controls
        self.init_ui()

    def init_ui(self):
        """
        Initialize the UI for the DigitalToneModifySection
        """
        layout = QVBoxLayout()
        self.setLayout(layout)

        attack_time_interval_sens = self._create_parameter_slider(
            AddressParameterDigitalModify.ATTACK_TIME_INTERVAL_SENS,
            "Attack Time Interval Sens",
        )
        layout.addWidget(attack_time_interval_sens)

        release_time_interval_sens = self._create_parameter_slider(
            AddressParameterDigitalModify.RELEASE_TIME_INTERVAL_SENS,
            "Release Time Interval Sens",
        )
        layout.addWidget(release_time_interval_sens)

        portamento_time_interval_sens = self._create_parameter_slider(
            AddressParameterDigitalModify.PORTAMENTO_TIME_INTERVAL_SENS,
            "Portamento Time Interval Sens",
        )
        layout.addWidget(portamento_time_interval_sens)

        envelope_loop_mode_row = QHBoxLayout()
        envelope_loop_mode = self._create_parameter_combo_box(
            AddressParameterDigitalModify.ENVELOPE_LOOP_MODE,
            "Envelope Loop Mode",
            ["OFF", "FREE-RUN", "TEMPO-SYNC"],
        )
        envelope_loop_mode_row.addWidget(envelope_loop_mode)
        layout.addLayout(envelope_loop_mode_row)

        envelope_loop_sync_note_row = QHBoxLayout()
        envelope_loop_sync_note = self._create_parameter_combo_box(
            AddressParameterDigitalModify.ENVELOPE_LOOP_SYNC_NOTE,
            "Envelope Loop Sync Note",
            LFOSyncNote.get_all_display_names(),
        )
        envelope_loop_sync_note_row.addWidget(envelope_loop_sync_note)
        layout.addLayout(envelope_loop_sync_note_row)

        chromatic_portamento_row = QHBoxLayout()
        chromatic_portamento_label = QLabel("Chromatic Portamento")
        chromatic_portamento_row.addWidget(chromatic_portamento_label)

        chromatic_portamento = self._create_parameter_switch(
            AddressParameterDigitalModify.CHROMATIC_PORTAMENTO,
            "Chromatic Portamento",
            ["OFF", "ON"],
        )
        layout.addWidget(chromatic_portamento)

        layout.addStretch()
