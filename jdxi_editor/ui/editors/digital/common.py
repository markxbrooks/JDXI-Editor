"""
Digital Synth Editor for the Roland JD-Xi.

This module provides the UI components for editing digital synth parameters on the Roland JD-Xi.
The editor supports three partials (voices) with individual parameter control and common parameters
that affect all partials.

Classes:
    DigitalSynthEditor: Main editor class for digital synth parameters
        - Handles MIDI communication for parameter changes
        - Manages UI state for all digital synth controls
        - Provides preset loading and management
        - Supports real-time parameter updates via SysEx

Features:
    - Three independent partial editors
    - Common parameter controls (portamento, unison, legato, etc.)
    - Preset management and loading
    - Real-time MIDI parameter updates
    - ADSR envelope controls for both amplitude and filter
    - Oscillator waveform selection
    - Partial enabling/disabling and selection

Dependencies:
    - PySide6 for UI components
    - qtawesome for icons
    - Custom MIDI handling classes
    - Digital synth parameter definitions

"""

import json
import logging
from typing import Dict, Optional, Union

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QTabWidget,
    QScrollArea,
    QLabel,
    QPushButton,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QShortcut, QKeySequence
import qtawesome as qta

from jdxi_editor.midi.data.lfo.lfo import LFOSyncNote
from jdxi_editor.midi.data.parsers.util import COMMON_IGNORED_KEYS
from jdxi_editor.midi.data.presets.digital import DIGITAL_PRESETS_ENUMERATED
from jdxi_editor.midi.data.programs.presets import DIGITAL_PRESET_LIST
from jdxi_editor.midi.preset.type import SynthType
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.midi.sysex.requests import DIGITAL1_REQUESTS, DIGITAL2_REQUESTS
from jdxi_editor.midi.utils.conversions import midi_cc_to_ms, midi_cc_to_frac
from jdxi_editor.ui.editors.helpers.program import get_preset_parameter_value, log_midi_info
from jdxi_editor.ui.editors.synth.editor import SynthEditor, _log_changes
from jdxi_editor.ui.editors.digital.partial import DigitalPartialEditor
from jdxi_editor.midi.data.parameter.digital.modify import DigitalModifyParameter
from jdxi_editor.ui.style import Style
from jdxi_editor.ui.widgets.display.digital import DigitalDisplay, DigitalTitle
from jdxi_editor.ui.widgets.preset.combo_box import PresetComboBox
from jdxi_editor.midi.data.digital import (
    DigitalOscWave,
    DigitalPartial,
    set_partial_state,
    get_digital_parameter_by_address,
)
from jdxi_editor.midi.data.parameter.digital.common import DigitalCommonParameter
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParameter
from jdxi_editor.midi.data.constants import (
    TEMPORARY_DIGITAL_SYNTH_1_AREA,
    COMMON_AREA,
)
from jdxi_editor.midi.data.constants.constants import MIDI_CHANNEL_DIGITAL1, MIDI_CHANNEL_DIGITAL2, DIGITAL_1_PART, \
    DIGITAL_2_PART
from jdxi_editor.midi.data.constants.sysex import DIGITAL_SYNTH_1_AREA, DIGITAL_SYNTH_2_AREA, \
    TEMPORARY_DIGITAL_SYNTH_2_AREA
from jdxi_editor.ui.widgets.switch.partial import PartialsPanel


class DigitalCommonEditor(SynthEditor):
    """class for Digital Synth Editor containing 3 partials"""

    preset_changed = Signal(int, str, int)

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        synth_num=1,
        parent=None,
        preset_helper=None,
    ):
        super().__init__(parent)
        # Image display
        self.partial_num = None
        self.current_data = None
        self.preset_type = (
            SynthType.DIGITAL_1 if synth_num == 1 else SynthType.DIGITAL_2
        )

        self.presets = DIGITAL_PRESETS_ENUMERATED
        self.instrument_image_label = QLabel()
        self.instrument_image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center align the image
        self.instrument_default_image = "jdxi_vector.png"
        self.midi_helper = midi_helper
        self.preset_helper = preset_helper
        self.midi_requests = DIGITAL1_REQUESTS if synth_num == 1 else DIGITAL2_REQUESTS
        self.instrument_icon_folder = "digital_synths"
        if preset_helper:
            self.preset_helper = preset_helper
        else:
            if self.preset_type == SynthType.DIGITAL_1:
                self.preset_helper = parent.digital_1_preset_helper
            else:
                self.preset_helper = parent.digital_2_preset_helper
        self.synth_num = synth_num
        if self.synth_num == 2:
            self.midi_channel = MIDI_CHANNEL_DIGITAL2
            self.area = TEMPORARY_DIGITAL_SYNTH_2_AREA
            self.part = DIGITAL_2_PART
        else:
            self.midi_channel = MIDI_CHANNEL_DIGITAL1
            self.area = TEMPORARY_DIGITAL_SYNTH_1_AREA
            self.part = DIGITAL_1_PART
        # midi message parameters

        self.group = COMMON_AREA
        self.setWindowTitle(f"Digital Synth {synth_num}")
        self.main_window = parent

        # Store parameter controls for easy access
        self.controls: Dict[
            Union[DigitalPartialParameter, DigitalCommonParameter], QWidget
        ] = {}

        # Allow resizing
        self.setMinimumSize(800, 300)
        self.resize(930, 600)

        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        self.setStyleSheet(Style.JDXI_TABS + Style.JDXI_EDITOR)
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Create container widget
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        upper_layout = QHBoxLayout()
        container_layout.addLayout(upper_layout)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # Title and instrument selection
        instrument_preset_group = QGroupBox("Digital Synth")
        #self.instrument_title_label = QLabel(
        #    f"Current Tone:\n {self.presets[0]}" if self.presets else "Current Tone:"
        #)
        self.instrument_title_label = DigitalTitle()
        self.instrument_title_label.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
        """
        )
        instrument_title_group_layout = QVBoxLayout()
        instrument_preset_group.setLayout(instrument_title_group_layout)
        # instrument_title_group_layout.addWidget(self.instrument_title_label)

        self.instrument_selection_label = QLabel("Select address digital synth:")
        instrument_title_group_layout.addWidget(self.instrument_selection_label)
        # Synth selection
        upper_layout = QHBoxLayout()
        container_layout.addLayout(upper_layout)

        # Title and drum kit selection
        instrument_preset_group = QGroupBox("Digital Synth")
        self.instrument_title_label = QLabel(
            self.presets[0] if self.presets else ""
        )
        instrument_preset_group.setStyleSheet("""
                        width: 100px;
        """)
        # self.instrument_title_label = DigitalDisplay()
        # self.instrument_title_label.setStyleSheet(Style.JDXI_INSTRUMENT_TITLE_LABEL)
        self.instrument_title_label = DigitalTitle()
        #self.instrument_title_label.setStyleSheet(Style.JDXI_INSTRUMENT_TITLE_LABEL
        #)
        instrument_title_group_layout = QVBoxLayout()
        instrument_preset_group.setLayout(instrument_title_group_layout)
        instrument_title_group_layout.addWidget(self.instrument_title_label)

        # Add the "Read Request" button
        self.read_request_button = QPushButton("Send Read Request to Synth")
        self.read_request_button.clicked.connect(self.data_request)
        instrument_title_group_layout.addWidget(self.read_request_button)

        self.instrument_selection_label = QLabel("Select preset for Digital synth:")
        instrument_title_group_layout.addWidget(self.instrument_selection_label)
        # Synth selection
        # Preset ComboBox
        self.instrument_selection_combo = PresetComboBox(DIGITAL_PRESET_LIST)
        self.instrument_selection_combo.combo_box.setEditable(True)  # Allow text search
        self.instrument_selection_combo.combo_box.setCurrentIndex(
            self.preset_helper.current_preset_zero_indexed
        )
        self.instrument_selection_combo.preset_loaded.connect(self.load_preset)

        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_image
        )
        # Connect QComboBox signal to PresetHandler
        self.preset_helper.preset_changed.connect(self.update_combo_box_index)
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_title
        )
        self.instrument_selection_combo.load_button.clicked.connect(
            self.update_instrument_preset
        )
        instrument_title_group_layout.addWidget(self.instrument_selection_combo)
        upper_layout.addWidget(instrument_preset_group)
        upper_layout.addWidget(self.instrument_image_label)
        container_layout.addLayout(upper_layout)
        self.update_instrument_image()

        # Add partials panel at the top
        self.partials_panel = PartialsPanel()
        container_layout.addWidget(self.partials_panel)
        self.partials_panel.setStyleSheet(Style.JDXI_TABS)

        # Create tab widget for partials
        self.partial_tab_widget = QTabWidget()
        self.partial_tab_widget.setStyleSheet(Style.JDXI_TABS + Style.JDXI_EDITOR)
        self.partial_editors = {}

        # Create editor for each partial
        for i in range(1, 4):
            editor = DigitalPartialEditor(midi_helper, i, self.part)
            self.partial_editors[i] = editor
            self.partial_tab_widget.addTab(editor, f"Partial {i}")
        self.partial_tab_widget.addTab(
            self._create_common_controls_section(), "Common Controls"
        )
        self.partial_tab_widget.addTab(self._create_tone_modify_section(), "Tone Modify")

        container_layout.addWidget(self.partial_tab_widget)

        # Add container to scroll area
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # Connect partial switches to enable/disable tabs
        for switch in self.partials_panel.switches.values():
            switch.stateChanged.connect(self._on_partial_state_changed)
        self.midi_helper.midi_parameter_received.connect(self._on_parameter_received)
        # Initialize with default states
        self.initialize_partial_states()
        self.data_request()

        # Register the callback for incoming MIDI messages
        if self.midi_helper:
            logging.info("MIDI helper initialized")
        else:
            logging.error("MIDI helper not initialized")
        print(f"self.controls: {self.controls}")
        self.refresh_shortcut = QShortcut(QKeySequence.StandardKey.Refresh, self)
        self.refresh_shortcut.activated.connect(self.data_request)
        if self.midi_helper:
            self.midi_helper.midi_program_changed.connect(self._handle_program_change)
            self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
        self.show()
        if self.synth_num == 2:
            self.midi_helper.update_digital2_tone_name.connect(self.set_instrument_title_label)
        else:
            self.midi_helper.update_digital1_tone_name.connect(self.set_instrument_title_label)

    def update_instrument_title(self, text):
        self.instrument_title_label.setText(text)

    def _create_common_controls_section(self):
        """Create common controls section"""
        group = QWidget()
        # area = QGroupBox("Common Controls")
        layout = QVBoxLayout()
        group.setLayout(layout)
        # prettify with icons

        icons_hlayout = QHBoxLayout()
        for icon in [
            "ph.bell-ringing-bold",
            "mdi.call-merge",
            "mdi.account-voice",
            "ri.voiceprint-fill",
            "mdi.piano",
        ]:
            icon_label = QLabel()
            icon = qta.icon(icon, color="#666666")
            pixmap = icon.pixmap(
                Style.ICON_SIZE, Style.ICON_SIZE
            )  # Set the desired size
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignHCenter)
            icons_hlayout.addWidget(icon_label)
        layout.addLayout(icons_hlayout)

        mono_switch_row = QHBoxLayout()
        self.mono_switch = self._create_parameter_switch(DigitalCommonParameter.MONO_SWITCH, "Mono",
                                                         ["OFF", "ON"])
        mono_switch_row.addWidget(self.mono_switch)
        layout.addLayout(mono_switch_row)

        self.pitch_bend_row = QHBoxLayout()
        self.pitch_bend_up = self._create_parameter_slider(
            DigitalCommonParameter.PITCH_BEND_UP, "Pitch Bend Up"
        )
        self.pitch_bend_down = self._create_parameter_slider(
            DigitalCommonParameter.PITCH_BEND_DOWN, "Pitch Bend Down"
        )
        self.pitch_bend_row.addWidget(self.pitch_bend_up)
        self.pitch_bend_row.addWidget(self.pitch_bend_down)
        layout.addLayout(self.pitch_bend_row)

        # Create tone level row
        self.tone_level_row = QHBoxLayout()
        self.tone_level = self._create_parameter_slider(
            DigitalCommonParameter.TONE_LEVEL, "Tone Level"
        )
        self.tone_level_row.addWidget(self.tone_level)
        layout.addLayout(self.tone_level_row)

        # Ring Modulator switch
        self.ring_row = QHBoxLayout()
        self.ring_switch = self._create_parameter_switch(DigitalCommonParameter.RING_SWITCH, "Ring", ["OFF", "---", "ON"])
        self.ring_row.addWidget(self.ring_switch)
        layout.addLayout(self.ring_row)

        # Unison switch and size
        self.unison_switch_row = QHBoxLayout()
        self.unison_switch = self._create_parameter_switch(DigitalCommonParameter.UNISON_SWITCH,
                                                           "Unison",
                                                           ["OFF", "ON"])
        self.unison_switch_row.addWidget(self.unison_switch)
        layout.addLayout(self.unison_switch_row)

        self.unison_size = self._create_parameter_switch(DigitalCommonParameter.UNISON_SIZE,
                                                         "Size",
                                                         ["2 VOICE", "3 VOICE", "4 VOICE", "5 VOICE"])
        self.unison_switch_row.addWidget(self.unison_size)
        self.controls[DigitalCommonParameter.UNISON_SIZE] = self.unison_size
        layout.addLayout(self.unison_switch_row)

        self.portamento_row = QHBoxLayout()
        self.portamento_switch = self._create_parameter_switch(DigitalCommonParameter.PORTAMENTO_SWITCH,
                                                               "Portamento",
                                                               ["OFF", "ON"])
        self.portamento_row.addWidget(self.portamento_switch)
        layout.addLayout(self.portamento_row)

        self.portamento_time_row = QHBoxLayout()
        self.portamento_time = self._create_parameter_slider(
            DigitalCommonParameter.PORTAMENTO_TIME, "Portamento Time"
        )
        self.portamento_time_row.addWidget(self.portamento_time)
        self.controls[DigitalCommonParameter.PORTAMENTO_TIME] = self.portamento_time
        layout.addLayout(self.portamento_time_row)

        # Portamento mode and legato
        self.portamento_mode = self._create_parameter_switch(DigitalCommonParameter.PORTAMENTO_MODE,
                                                             "Portamento Mode",
                                                             ["NORMAL", "LEGATO"])
        self.portamento_row.addWidget(self.portamento_mode)

        self.legato_row = QHBoxLayout()
        self.legato_switch = self._create_parameter_switch(DigitalCommonParameter.LEGATO_SWITCH,
                                                           "Legato",
                                                           ["OFF", "ON"])
        self.legato_row.addWidget(self.legato_switch)

        # Analog Feel and Wave Shape
        self.analog_feel = self._create_parameter_slider(
            DigitalCommonParameter.ANALOG_FEEL, "Analog Feel"
        )
        self.wave_shape = self._create_parameter_slider(
            DigitalCommonParameter.WAVE_SHAPE, "Wave Shape"
        )
        self.controls[DigitalCommonParameter.ANALOG_FEEL] = self.analog_feel
        self.controls[DigitalCommonParameter.WAVE_SHAPE] = self.wave_shape
        # Add all controls to layout
        layout.addLayout(mono_switch_row)
        layout.addLayout(self.tone_level_row)
        layout.addLayout(self.ring_row)
        layout.addLayout(self.unison_switch_row)
        layout.addLayout(self.legato_row)
        layout.addWidget(self.analog_feel)
        layout.addWidget(self.wave_shape)
        self.update_instrument_image()
        return group
    
    def _create_tone_modify_section(self):
        """Create tone modify section"""
        group = QWidget()
        layout = QVBoxLayout()
        group.setLayout(layout)
        attack_time_interval_sens = self._create_parameter_slider(
            DigitalModifyParameter.ATTACK_TIME_INTERVAL_SENS, "Attack Time Interval Sens"
        )
        layout.addWidget(attack_time_interval_sens)
        release_time_interval_sens = self._create_parameter_slider(
            DigitalModifyParameter.RELEASE_TIME_INTERVAL_SENS, "Release Time Interval Sens"
        )
        layout.addWidget(release_time_interval_sens)
        portamento_time_interval_sens = self._create_parameter_slider(
            DigitalModifyParameter.PORTAMENTO_TIME_INTERVAL_SENS, "Portamento Time Interval Sens"
        )
        layout.addWidget(portamento_time_interval_sens)

        envelope_loop_mode_row = QHBoxLayout()
        envelope_loop_mode = self._create_parameter_combo_box(
            DigitalModifyParameter.ENVELOPE_LOOP_MODE, "Envelope Loop Mode", ["OFF", "FREE-RUN", "TEMPO-SYNC"]
        )
        envelope_loop_mode_row.addWidget(envelope_loop_mode)
        layout.addLayout(envelope_loop_mode_row)

        envelope_loop_sync_note_row = QHBoxLayout()
        envelope_loop_sync_note = self._create_parameter_combo_box(
            DigitalModifyParameter.ENVELOPE_LOOP_SYNC_NOTE, "Envelope Loop Sync Note",
            LFOSyncNote.get_all_display_names())
        envelope_loop_sync_note_row.addWidget(envelope_loop_sync_note)
        layout.addLayout(envelope_loop_sync_note_row)

        chromatic_portamento_row = QHBoxLayout()
        chromatic_portamento_label = QLabel("Chromatic Portamento")
        chromatic_portamento_row.addWidget(chromatic_portamento_label)
        chromatic_portamento = self._create_parameter_switch(
            DigitalModifyParameter.CHROMATIC_PORTAMENTO, "Chromatic Portamento", ["OFF", "ON"]
        )
        layout.addWidget(chromatic_portamento)
        layout.addStretch()
        return group

    def load_preset(self, preset_index):
        """Load a preset by program change."""
        preset_name = self.instrument_selection_combo.combo_box.currentText()  # Get the selected preset name
        logging.info(f"combo box preset_name : {preset_name}")
        program_number = preset_name[:3]
        logging.info(f"combo box program_number : {program_number}")

        # Get MSB, LSB, PC values from the preset using get_preset_parameter_value
        msb = get_preset_parameter_value("msb", program_number)
        lsb = get_preset_parameter_value("lsb", program_number)
        pc = get_preset_parameter_value("pc", program_number)

        if None in [msb, lsb, pc]:
            logging.error(f"Could not retrieve preset parameters for program {program_number}")
            return

        logging.info(f"retrieved msb, lsb, pc : {msb}, {lsb}, {pc}")
        log_midi_info(msb, lsb, pc)

        # Send bank select and program change
        # Note: PC is 0-based in MIDI, so subtract 1
        self.midi_helper.send_bank_select_and_program_change(
            self.midi_channel,  # MIDI channel
            msb,  # MSB is already correct
            lsb,  # LSB is already correct
            pc - 1  # Convert 1-based PC to 0-based
        )
        self.data_request()

    def _on_partial_state_changed(
        self, partial: DigitalPartial, enabled: bool, selected: bool
    ):
        """Handle partial state changes"""
        if self.midi_helper:
            set_partial_state(self.midi_helper, partial, enabled, selected)

        # Enable/disable corresponding tab
        partial_num = partial.value
        self.partial_tab_widget.setTabEnabled(partial_num - 1, enabled)

        # Switch to selected partial's tab
        if selected:
            self.partial_tab_widget.setCurrentIndex(partial_num - 1)

    def initialize_partial_states(self):
        """Initialize partial states with defaults"""
        # Default: Partial 1 enabled and selected, others disabled
        for partial in DigitalPartial.get_partials():
            enabled = partial == DigitalPartial.PARTIAL_1
            selected = enabled
            self.partials_panel.switches[partial].setState(enabled, selected)
            self.partial_tab_widget.setTabEnabled(partial.value - 1, enabled)

        # Show first tab
        self.partial_tab_widget.setCurrentIndex(0)

    def _on_parameter_received(self, address, value):
        """Handle parameter updates from MIDI messages."""
        area_code = address[0]
        if address[0] in [TEMPORARY_DIGITAL_SYNTH_1_AREA, DIGITAL_SYNTH_2_AREA]:
            # Extract the actual parameter address (80, 0) from [25, 1, 80, 0]
            parameter_address = tuple(address[2:])  # (80, 0)

            # Retrieve the corresponding DigitalParameter
            param = get_digital_parameter_by_address(parameter_address)
            partial_no = address[1]
            if param:
                logging.info(f"param: \t{param} \taddress=\t{address}, Value=\t{value}")

                # Update the corresponding slider
                if param in self.partial_editors[partial_no].controls:
                    slider_value = param.convert_from_midi(value)
                    logging.info(
                        f"midi value {value} converted to slider value {slider_value}"
                    )
                    slider = self.partial_editors[partial_no].controls[param]
                    slider.blockSignals(True)  # Prevent feedback loop
                    slider.setValue(slider_value)
                    slider.blockSignals(False)

                # Handle OSC_WAVE parameter to update waveform buttons
                if param == DigitalPartialParameter.OSC_WAVE:
                    self._update_waveform_buttons(partial_no, value)
                    logging.debug(
                        "updating waveform buttons for param {param} with {value}"
                    )

    def _update_partial_sliders_from_sysex(self, json_sysex_data: str):
        """Update sliders and combo boxes based on parsed SysEx data."""
        logging.info("Updating UI components from SysEx data")
        debug_param_updates = True
        debug_stats = True

        try:
            sysex_data = json.loads(json_sysex_data)
            self.previous_data = self.current_data
            self.current_data = sysex_data
            _log_changes(self.previous_data, sysex_data)
        except json.JSONDecodeError as ex:
            logging.error(f"Invalid JSON format: {ex}")
            return

        def _check_sysex_area(sysex_data):
            """Check if SysEx data belongs to address supported digital synth area."""
            temp_area = sysex_data.get("TEMPORARY_AREA")
            logging.info(f"@@@ TEMPORARY_AREA: {temp_area} self.area {self.area}")
            area_map = {
                TEMPORARY_DIGITAL_SYNTH_1_AREA: "TEMPORARY_DIGITAL_SYNTH_1_AREA",
                TEMPORARY_DIGITAL_SYNTH_2_AREA: "TEMPORARY_DIGITAL_SYNTH_2_AREA",
            }
            return temp_area == area_map.get(self.area)

        temporary_area = _check_sysex_area(sysex_data)
        if not temporary_area:
            logging.info(
                f"SysEx data does not belong to self.area {self.area}. "
                f"Skipping update. temporary_area: {temporary_area}"
            )
            return
        else:
            logging.info(f"SysEx data belongs to self.area {self.area} "
                         f"temporary_area: {temporary_area}")

        def _get_partial_number(synth_tone):
            """Retrieve partial number from synth tone mapping."""
            partial_map = {
                "PARTIAL_1": 1,
                "PARTIAL_2": 2,
                "PARTIAL_3": 3,
                "TONE_PARTIAL_1": 1,
                "TONE_PARTIAL_2": 2,
                "TONE_PARTIAL_3": 3
            }
            partial_no = partial_map.get(synth_tone)
            logging.info(f"partial_no: {partial_no}")
            if partial_no is None:
                logging.warning(f"Unknown synth tone: {synth_tone}")
            return partial_no

        def update_adsr_widget(param, value):
            """Helper function to update ADSR widgets."""
            new_value = (
                midi_cc_to_frac(value)
                if param
                in [
                    DigitalPartialParameter.AMP_ENV_SUSTAIN_LEVEL,
                    DigitalPartialParameter.FILTER_ENV_SUSTAIN_LEVEL,
                ]
                else midi_cc_to_ms(value)
            )

            adsr_mapping = {
                DigitalPartialParameter.AMP_ENV_ATTACK_TIME: self.partial_editors[
                    partial_no
                ].amp_env_adsr_widget.attack_sb,
                DigitalPartialParameter.AMP_ENV_DECAY_TIME: self.partial_editors[
                    partial_no
                ].amp_env_adsr_widget.decay_sb,
                DigitalPartialParameter.AMP_ENV_SUSTAIN_LEVEL: self.partial_editors[
                    partial_no
                ].amp_env_adsr_widget.sustain_sb,
                DigitalPartialParameter.AMP_ENV_RELEASE_TIME: self.partial_editors[
                    partial_no
                ].amp_env_adsr_widget.release_sb,
                DigitalPartialParameter.FILTER_ENV_ATTACK_TIME: self.partial_editors[
                    partial_no
                ].filter_adsr_widget.attack_sb,
                DigitalPartialParameter.FILTER_ENV_DECAY_TIME: self.partial_editors[
                    partial_no
                ].filter_adsr_widget.decay_sb,
                DigitalPartialParameter.FILTER_ENV_SUSTAIN_LEVEL: self.partial_editors[
                    partial_no
                ].filter_adsr_widget.sustain_sb,
                DigitalPartialParameter.FILTER_ENV_RELEASE_TIME: self.partial_editors[
                    partial_no
                ].filter_adsr_widget.release_sb,
            }

            if param in adsr_mapping:
                spinbox = adsr_mapping[param]
                spinbox.setValue(new_value)
        """ 
        temporary_area = _check_sysex_area(sysex_data)
        if not temporary_area:
            logging.info(
                "SysEx data does not belong to self.area {self.area}. "
                "Skipping update. temporary_area: {temporary_area}"
            )
            return
        else:
            logging.info(f"SysEx data belongs to self.area {self.area} "
                         f"temporary_area: {temporary_area}")
        """
        synth_tone = sysex_data.get("SYNTH_TONE")
        partial_no = _get_partial_number(synth_tone)

        ignored_keys = {
            "JD_XI_HEADER",
            "ADDRESS",
            "TEMPORARY_AREA",
            "TONE_NAME",
            "SYNTH_TONE",
        }
        sysex_data = {k: v for k, v in sysex_data.items() if k not in ignored_keys}

        osc_waveform_map = {wave.value: wave for wave in DigitalOscWave}

        failures, successes = [], []

        def _update_slider(param, value):
            """Helper function to update sliders safely."""
            slider = self.partial_editors[partial_no].controls.get(param)
            if slider:
                slider_value = param.convert_from_midi(value)
                logging.info(
                    f"midi value {value} converted to slider value {slider_value}"
                )
                slider.blockSignals(True)
                slider.setValue(slider_value)
                slider.blockSignals(False)
                successes.append(param.name)
                if debug_param_updates:
                    logging.info(f"Updated: {param.name:50} {value}")

        def _update_waveform(param_value):
            """Helper function to update waveform selection UI."""
            waveform = osc_waveform_map.get(param_value)
            if waveform and waveform in self.partial_editors[partial_no].wave_buttons:
                button = self.partial_editors[partial_no].wave_buttons[waveform]
                button.setChecked(True)
                self.partial_editors[partial_no]._on_waveform_selected(waveform)
                logging.debug(f"Updated waveform button for {waveform}")

        for param_name, param_value in sysex_data.items():
            param = DigitalPartialParameter.get_by_name(param_name)

            if param:
                if param == DigitalPartialParameter.OSC_WAVE:
                    self._update_waveform_buttons(partial_no, param_value)
                else:
                    _update_slider(param, param_value)
                    update_adsr_widget(param, param_value)
            else:
                failures.append(param_name)

        def _log_debug_info():
            """Helper function to log debugging statistics."""
            if debug_stats:
                success_rate = (
                    (len(successes) / len(sysex_data) * 100) if sysex_data else 0
                )
                logging.info(f"Successes: {successes}")
                logging.info(f"Failures: {failures}")
                logging.info(f"Success Rate: {success_rate:.1f}%")
                logging.info("--------------------------------")

        _log_debug_info()

    def _update_partial_sliders_from_sysex_new(self, json_sysex_data: str):
        """Update sliders and combo boxes based on parsed SysEx data."""
        logging.info("Updating UI components from SysEx data")
        debug_param_updates = True
        debug_stats = True

        try:
            sysex_data = json.loads(json_sysex_data)
            self.previous_data = self.current_data
            self.current_data = sysex_data
            _log_changes(self.previous_data, sysex_data)
        except json.JSONDecodeError as ex:
            logging.error(f"Invalid JSON format: {ex}")
            return

        def _is_valid_sysex_area(sysex_data):
            """Check if SysEx data belongs to address supported digital synth area."""
            return sysex_data.get("TEMPORARY_AREA") in [
                "TEMPORARY_DIGITAL_SYNTH_1_AREA",
                "TEMPORARY_DIGITAL_SYNTH_2_AREA",
            ]

        def _get_partial_number(synth_tone):
            """Retrieve partial number from synth tone mapping."""
            partial_map = {
                "PARTIAL_1": 1,
                "PARTIAL_2": 2,
                "PARTIAL_3": 3,
                "TONE_PARTIAL_1": 1,
                "TONE_PARTIAL_2": 2,
                "TONE_PARTIAL_3": 3
            }
            partial_no = partial_map.get(synth_tone)
            if partial_no is None:
                logging.warning(f"Unknown synth tone: {synth_tone}")
            return partial_no

        def _update_slider(param, value):
            """Helper function to update sliders safely."""
            if partial_no is None:
                logging.warning("Cannot update slider: partial_no is None")
                return

            if partial_no not in self.partial_editors:
                logging.warning(f"Partial editor {partial_no} not found")
                return

            slider = self.partial_editors[partial_no].controls.get(param)
            if slider:
                slider_value = param.convert_from_midi(value)
                logging.info(f"midi value {value} converted to slider value {slider_value}")
                slider.blockSignals(True)
                slider.setValue(slider_value)
                slider.blockSignals(False)
                successes.append(param.name)
                if debug_param_updates:
                    logging.info(f"Updated: {param.name:50} {value}")
            else:
                failures.append(param.name)

        if not _is_valid_sysex_area(sysex_data):
            logging.warning(
                "SysEx data does not belong to TEMPORARY_DIGITAL_SYNTH_1_AREA or TEMPORARY_DIGITAL_SYNTH_2_AREA. Skipping update."
            )
            return

        synth_tone = sysex_data.get("SYNTH_TONE")
        partial_no = _get_partial_number(synth_tone)

        if partial_no is None:
            logging.warning(f"Could not determine partial number from synth tone: {synth_tone}")
            return

        ignored_keys = {
            "JD_XI_HEADER",
            "ADDRESS",
            "TEMPORARY_AREA",
            "TONE_NAME",
            "SYNTH_TONE",
        }
        sysex_data = {k: v for k, v in sysex_data.items() if k not in ignored_keys}

        failures, successes = [], []

        for param_name, param_value in sysex_data.items():
            param = DigitalPartialParameter.get_by_name(param_name)

            if param:
                if param == DigitalPartialParameter.OSC_WAVE:
                    self._update_waveform_buttons(partial_no, param_value)
                else:
                    _update_slider(param, param_value)
                    # update_adsr_widget(param, param_value)
            else:
                failures.append(param_name)

        def _log_debug_info():
            """Helper function to log debugging statistics."""
            if debug_stats:
                success_rate = (len(successes) / len(sysex_data) * 100) if sysex_data else 0
                logging.info(f"Successes: {successes}")
                logging.info(f"Failures: {failures}")
                logging.info(f"Success Rate: {success_rate:.1f}%")
                logging.info("--------------------------------")

        _log_debug_info()

    def _dispatch_sysex_to_area(self, json_sysex_data: str):
        """Update sliders and combo boxes based on parsed SysEx data."""
        logging.info("Updating UI components from SysEx data")
        failures, successes = [], []

        def _parse_sysex_json(json_data):
            """Parse JSON safely and log changes."""
            try:
                sysex_dict = json.loads(json_data)
                return sysex_dict
            except json.JSONDecodeError as ex:
                logging.error(f"Invalid JSON format: {ex}")
                return None

        # Parse SysEx data
        sysex_data = _parse_sysex_json(json_sysex_data)
        if not sysex_data:
            return

        synth_tone = sysex_data.get("SYNTH_TONE")

        if synth_tone == "TONE_COMMON":
            logging.info("\nTone common")
            self._update_common_sliders_from_sysex(json_sysex_data)
        elif synth_tone == "TONE_MODIFY":
            pass  # not yet implemented
        elif synth_tone in ["PRC3"]: # This is for drums but comes through
            pass
        else:
            self._update_partial_sliders_from_sysex(json_sysex_data)

    def _update_common_sliders_from_sysex(self, json_sysex_data: str):
        """Update sliders and combo boxes based on parsed SysEx data."""
        logging.info("Updating UI components from SysEx data")
        debug_param_updates = True
        debug_stats = True
        failures, successes = [], []

        def _parse_sysex_json(json_data):
            """Parse JSON safely and log changes."""
            try:
                sysex_data = json.loads(json_data)
                self.previous_data = self.current_data
                self.current_data = sysex_data
                _log_changes(self.previous_data, sysex_data)
                return sysex_data
            except json.JSONDecodeError as ex:
                logging.error(f"Invalid JSON format: {ex}")
                return None

        def _is_valid_sysex_area(sysex_data):
            """Check if SysEx data belongs to address supported digital synth area."""
            temp_area = sysex_data.get("TEMPORARY_AREA")
            logging.info(f"temp_area: {temp_area}")
            return sysex_data.get("TEMPORARY_AREA") in [
                "TEMPORARY_DIGITAL_SYNTH_1_AREA",
                "TEMPORARY_DIGITAL_SYNTH_2_AREA",
            ]

        def _get_partial_number(synth_tone):
            """Retrieve partial number from synth tone mapping."""
            partial_map = {
                "PARTIAL_1": 1,
                "PARTIAL_2": 2,
                "PARTIAL_3": 3,
                "TONE_PARTIAL_1": 1,
                "TONE_PARTIAL_2": 2,
                "TONE_PARTIAL_3": 3
            }
            return partial_map.get(synth_tone, 3)

        def _update_common_slider(param, value):
            """Helper function to update sliders safely."""
            logging.info(f"param: {param}")
            slider = self.controls.get(param)
            logging.info(f"slider: {slider}")
            if slider:
                slider.blockSignals(True)
                slider.setValue(value)
                slider.blockSignals(False)
                successes.append(param.name)
                if debug_param_updates:
                    logging.info(f"Updated: {param.name:50} {value}")
            else:
                failures.append(param.name)

        def _update_common_switch(param, value):
            """Helper function to update checkbox safely."""
            logging.info(f"checkbox param: {param} {value}")
            partial_switch_map = {
                "PARTIAL1_SWITCH": 1,
                "PARTIAL2_SWITCH": 2,
                "PARTIAL3_SWITCH": 3,
            }
            partial_number = partial_switch_map.get(param_name)
            check_box = self.partials_panel.switches.get(partial_number)
            logging.info(f"check_box: {check_box}")
            if check_box:  # and isinstance(check_box, QCheckBox):
                check_box.blockSignals(True)
                check_box.setState(bool(value), False)
                check_box.blockSignals(False)
                successes.append(param.name)
                if debug_param_updates:
                    logging.info(f"Updated: {param.name:50} {value}")
            else:
                failures.append(param.name)

        # Parse SysEx data
        sysex_data = _parse_sysex_json(json_sysex_data)
        if not sysex_data:
            return

        if not _is_valid_sysex_area(sysex_data):
            logging.warning(
                "SysEx data does not belong to TEMPORARY_DIGITAL_SYNTH_1_AREA "
                "or TEMPORARY_DIGITAL_SYNTH_2_AREA. Skipping update."
            )
            return

        synth_tone = sysex_data.get("SYNTH_TONE")
        partial_no = _get_partial_number(sysex_data.get("SYNTH_TONE"))

        sysex_data = {
            k: v for k, v in sysex_data.items() if k not in COMMON_IGNORED_KEYS
        }

        if synth_tone == "TONE_COMMON":
            logging.info("\nTone common")
            for param_name, param_value in sysex_data.items():
                param = DigitalCommonParameter.get_by_name(param_name)
                logging.info(f"Tone common: param_name: {param} {param_value}")
                try:
                    if param:
                        if param_name in [
                            "PARTIAL1_SWITCH",
                            "PARTIAL1_SELECT",
                            "PARTIAL2_SWITCH",
                            "PARTIAL2_SELECT",
                            "PARTIAL3_SWITCH",
                            "PARTIAL3_SELECT",
                        ]:
                            _update_common_switch(param, param_value)
                        else:
                            _update_common_slider(param, param_value)
                    else:
                        failures.append(param_name)
                except Exception as ex:
                    logging.info(f"Error {ex} occurred")

        logging.info(f"Updating sliders for Partial {partial_no}")

        def _update_slider(param, value):
            """Helper function to update sliders safely."""
            slider = self.partial_editors[partial_no].controls.get(param)
            if slider:
                slider.blockSignals(True)
                slider.setValue(value)
                slider.blockSignals(False)
                successes.append(param.name)
                if debug_param_updates:
                    logging.info(f"Updated: {param.name:50} {value}")
            else:
                failures.append(param.name)

        def _log_debug_info():
            """Helper function to log debugging statistics."""
            if debug_stats:
                success_rate = (
                    (len(successes) / len(sysex_data) * 100) if sysex_data else 0
                )
                logging.info(f"successes: \t{successes}")
                logging.info(f"failures: \t{failures}")
                logging.info(f"success rate: \t{success_rate:.1f}%")
                logging.info("--------------------------------")

        _log_debug_info()

    def _update_waveform_buttons(self, partial_number, value):
        """Update the waveform buttons based on the OSC_WAVE value with visual feedback."""
        logging.debug(
            f"Updating waveform buttons for partial {partial_number} with value {value}"
        )

        if partial_number is None:
            logging.warning("Cannot update waveform buttons: partial_number is None")
            return

        waveform_map = {
            0: DigitalOscWave.SAW,
            1: DigitalOscWave.SQUARE,
            2: DigitalOscWave.PW_SQUARE,
            3: DigitalOscWave.TRIANGLE,
            4: DigitalOscWave.SINE,
            5: DigitalOscWave.NOISE,
            6: DigitalOscWave.SUPER_SAW,
            7: DigitalOscWave.PCM,
        }

        selected_waveform = waveform_map.get(value)

        if selected_waveform is None:
            logging.warning(f"Unknown waveform value: {value}")
            return

        logging.debug(f"Waveform value {value} found, selecting {selected_waveform}")

        # Retrieve waveform buttons for the given partial
        if partial_number not in self.partial_editors:
            logging.warning(f"Partial editor {partial_number} not found")
            return

        wave_buttons = self.partial_editors[partial_number].wave_buttons

        # Reset all buttons to default style
        for btn in wave_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(Style.JDXI_BUTTON_RECT)

        # Apply active style to the selected waveform button
        selected_btn = wave_buttons.get(selected_waveform)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(Style.JDXI_BUTTON_RECT)
        else:
            logging.warning(f"Waveform button not found for {selected_waveform}")
