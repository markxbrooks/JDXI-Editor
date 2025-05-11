"""
    Digital Tone Modify Section
"""

from typing import Callable
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFormLayout

from jdxi_editor.midi.data.lfo.lfo import LFOSyncNote
from jdxi_editor.midi.data.parameter.digital.modify import AddressParameterDigitalModify
from jdxi_editor.midi.data.parameter.effects.effects import AddressParameterEffect


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

        # effect1_section = self._create_effect1_section()
        # layout.addWidget(effect1_section)
        layout.addStretch()

    def _create_effect1_section(self):
        """Create Effect 1 section"""
        widget = QWidget()
        layout = QFormLayout()
        widget.setLayout(layout)

        # Create address combo box for EFX1 preset_type
        self.efx1_type = self._create_parameter_combo_box(
            AddressParameterEffect.EFX1_TYPE,
            "Effect 1 Type",
            ["Thru", "DISTORTION", "FUZZ", "COMPRESSOR", "BIT CRUSHER"],
            [0, 1, 2, 3, 4],
        )
        layout.addRow(self.efx1_type)

        # Create sliders for EFX1 parameters
        self.efx1_level = self._create_parameter_slider(
            AddressParameterEffect.EFX1_LEVEL, "EFX1 Level (0-127)"
        )
        layout.addRow(self.efx1_level)

        self.efx1_delay_send_level = self._create_parameter_slider(
            AddressParameterEffect.EFX1_DELAY_SEND_LEVEL,
            "EFX1 Delay Send Level (0-127)",
        )
        layout.addRow(self.efx1_delay_send_level)

        self.efx1_reverb_send_level = self._create_parameter_slider(
            AddressParameterEffect.EFX1_REVERB_SEND_LEVEL,
            "EFX1 Reverb Send Level (0-127)",
        )
        layout.addRow(self.efx1_reverb_send_level)

        self.efx1_output_assign = self._create_parameter_switch(
            AddressParameterEffect.EFX1_OUTPUT_ASSIGN, "Output Assign", ["DIR", "EFX2"]
        )
        layout.addRow(self.efx1_output_assign)

        self.efx1_parameter1_slider = self._create_parameter_slider(
            AddressParameterEffect.EFX1_PARAM_1, "Parameter 1"
        )
        layout.addRow(self.efx1_parameter1_slider)

        self.efx1_parameter2_slider = self._create_parameter_slider(
            AddressParameterEffect.EFX1_PARAM_2, "Parameter 2"
        )
        layout.addRow(self.efx1_parameter2_slider)

        self.efx1_parameter32_slider = self._create_parameter_slider(
            AddressParameterEffect.EFX1_PARAM_32, "Parameter 32"
        )
        layout.addRow(self.efx1_parameter32_slider)

        return widget
