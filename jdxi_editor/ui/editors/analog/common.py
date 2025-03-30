"""
Module: analog_synth_editor
===========================

This module defines the `AnalogSynthEditor` class, which provides a PySide6-based
user interface for editing analog synthesizer parameters in the Roland JD-Xi synthesizer.
It extends the `SynthEditor` base class and integrates MIDI communication for real-time
parameter adjustments and preset management.

Key Features:
-------------
- Provides a graphical editor for modifying analog synth parameters, including
  oscillator, filter, amp, LFO, and envelope settings.
- Supports MIDI communication to send and receive real-time parameter changes.
- Allows selection of different analog synth presets from a dropdown menu.
- Displays an instrument image that updates based on the selected preset.
- Includes a scrollable layout for managing a variety of parameter controls.
- Implements bipolar parameter handling for proper UI representation.
- Supports waveform selection with custom buttons and icons.
- Provides a "Send Read Request to Synth" button to retrieve current synth settings.
- Enables MIDI-triggered updates via incoming program changes and parameter adjustments.

Dependencies:
-------------
- PySide6 (for UI components and event handling)
- MIDIHelper (for handling MIDI communication)
- PresetHandler (for managing synth presets)
- Various custom enums and helper classes (AnalogParameter, AnalogCommonParameter, etc.)

Usage:
------
The `AnalogSynthEditor` class can be instantiated as part of a larger PySide6 application.
It requires a `MIDIHelper` instance for proper communication with the synthesizer.

Example:
--------
    midi_helper = MIDIHelper()
    preset_helper = PresetHandler()
    editor = AnalogSynthEditor(midi_helper, preset_helper)
    editor.show()
    
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel, QTabWidget, QGroupBox, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence

from jdxi_editor.ui.sections.oscillator_section import OscillatorSection
from jdxi_editor.ui.sections.filter_section import FilterSection
from jdxi_editor.ui.sections.amp_section import AmpSection
from jdxi_editor.ui.sections.lfo_section import LFOSection

class AnalogCommonEditor(SynthEditor):
    def __init__(self, midi_helper: Optional[MidiIOHelper], preset_helper=None, parent=None):
        super().__init__(midi_helper, parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Analog Synth")
        self.setMinimumSize(800, 600)
        self.resize(900, 600)
        self.setStyleSheet(Style.JDXI_TABS_ANALOG + Style.JDXI_EDITOR_ANALOG)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Main layout
        main_layout.addLayout(self.create_instrument_selection_layout())

        # Create scroll area for resizable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)

        self.tab_widget = QTabWidget()
        container_layout.addWidget(self.tab_widget)

        self.tab_widget.addTab(OscillatorSection(self.controls), "Oscillator")
        self.tab_widget.addTab(FilterSection(self.controls), "Filter")
        self.tab_widget.addTab(AmpSection(self.controls), "Amp")
        self.tab_widget.addTab(LFOSection(self.controls), "LFO")

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def create_instrument_selection_layout(self):
        upper_layout = QHBoxLayout()
        instrument_preset_group = QGroupBox("Analog Synth")
        self.instrument_title_label = QLabel("Analog Synth")
        instrument_title_group_layout = QVBoxLayout()
        instrument_preset_group.setLayout(instrument_title_group_layout)
        instrument_title_group_layout.addWidget(self.instrument_title_label)

        self.read_request_button = QPushButton("Send Read Request to Synth")
        self.read_request_button.clicked.connect(self.data_request)
        instrument_title_group_layout.addWidget(self.read_request_button)

        self.instrument_selection_label = QLabel("Select an Analog synth:")
        instrument_title_group_layout.addWidget(self.instrument_selection_label)
        self.instrument_selection_combo = PresetComboBox(ANALOG_PRESET_LIST)
        self.instrument_selection_combo.setEditable(True)
        self.instrument_selection_combo.currentIndexChanged.connect(self.update_instrument_image)
        self.instrument_selection_combo.currentIndexChanged.connect(self.update_instrument_title)
        self.instrument_selection_combo.load_button.clicked.connect(self.update_instrument_preset)
        instrument_title_group_layout.addWidget(self.instrument_selection_combo)

        upper_layout.addWidget(instrument_preset_group)
        self.instrument_image_label = QLabel()
        self.instrument_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upper_layout.addWidget(self.instrument_image_label)

        return upper_layout

    # ... Additional methods for handling UI updates

"""

import json
import logging
from typing import Optional, Dict, Union

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QScrollArea,
    QPushButton,
    QSlider,
    QTabWidget,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QShortcut, QKeySequence
import qtawesome as qta

from jdxi_editor.midi.data.presets.analog import ANALOG_PRESETS_ENUMERATED
from jdxi_editor.midi.data.programs.analog import ANALOG_PRESET_LIST
from jdxi_editor.midi.preset.type import SynthType
from jdxi_editor.midi.data.parameter.analog import AnalogParameter
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.midi.sysex.requests import PROGRAM_COMMON_REQUEST, ANALOG_REQUEST
from jdxi_editor.midi.utils.conversions import (
    midi_cc_to_ms,
    midi_cc_to_frac,
    frac_to_midi_cc,
    ms_to_midi_cc,
)
from jdxi_editor.midi.data.constants.sysex import TEMPORARY_TONE_AREA, TEMPORARY_ANALOG_SYNTH_AREA
from jdxi_editor.midi.data.constants.analog import (
    Waveform,
    SubOscType,
    ANALOG_PART,
    ANALOG_OSC_GROUP, LFO_TEMPO_SYNC_NOTES,
)
from jdxi_editor.midi.data.constants.constants import MIDI_CHANNEL_ANALOG
from jdxi_editor.ui.editors.helpers.analog import get_analog_parameter_by_address
from jdxi_editor.ui.editors.synth.editor import SynthEditor, _log_changes
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.ui.style import Style
from jdxi_editor.ui.widgets.adsr.adsr import ADSR
from jdxi_editor.ui.widgets.button.waveform.analog import AnalogWaveformButton
from jdxi_editor.ui.widgets.preset.combo_box import PresetComboBox


class AnalogCommonEditor(SynthEditor):
    """Analog Synth"""

    # preset_changed = Signal(int, str, int)

    def __init__(
            self, midi_helper: Optional[MidiIOHelper], preset_helper=None, parent=None
    ):
        super().__init__(midi_helper, parent)
        self.bipolar_parameters = [
            AnalogParameter.LFO_PITCH_DEPTH,
            AnalogParameter.LFO_FILTER_DEPTH,
            AnalogParameter.LFO_AMP_DEPTH,
            AnalogParameter.FILTER_ENV_VELOCITY_SENSITIVITY,
            AnalogParameter.AMP_LEVEL_VELOCITY_SENSITIVITY,
            AnalogParameter.AMP_LEVEL_KEYFOLLOW,
            AnalogParameter.OSC_PITCH_ENV_VELOCITY_SENSITIVITY,
            AnalogParameter.OSC_PITCH_COARSE,
            AnalogParameter.OSC_PITCH_FINE,
            AnalogParameter.LFO_PITCH_MODULATION_CONTROL,
            AnalogParameter.LFO_AMP_MODULATION_CONTROL,
            AnalogParameter.LFO_FILTER_MODULATION_CONTROL,
            AnalogParameter.LFO_RATE_MODULATION_CONTROL,
            AnalogParameter.LFO_PITCH_MODULATION_CONTROL,
            AnalogParameter.OSC_PITCH_ENV_DEPTH,
            AnalogParameter.FILTER_ENV_DEPTH,
            # Add other bipolar parameters as needed
        ]
        # Define parameter mappings
        self.cc_parameters = {
            "Cutoff": 102,
            "Resonance": 105,
            "Level": 117,
            "LFO Rate": 16,
        }
        self.nrpn_parameters = {
            "Envelope": (0, 124),
            "LFO Shape": (0, 3),
            "LFO Pitch Depth": (0, 15),
            "LFO Filter Depth": (0, 18),
            "LFO Amp Depth": (0, 21),
            "Pulse Width": (0, 37),
        }
        # NRPN Address Mapping
        self.nrpn_map = {
            (0, 124): "Envelope",
            (0, 3): "LFO Shape",
            (0, 15): "LFO Pitch Depth",
            (0, 18): "LFO Filter Depth",
            (0, 21): "LFO Amp Depth",
            (0, 37): "Pulse Width",
        }
        self.area = TEMPORARY_TONE_AREA
        self.group = ANALOG_OSC_GROUP
        self.part = ANALOG_PART
        self.preset_helper = preset_helper
        self.preset_type = SynthType.ANALOG
        self.setWindowTitle("Analog Synth")
        self.previous_json_data = None
        # Allow resizing
        self.setMinimumSize(800, 600)
        self.resize(900, 600)
        self.instrument_default_image = "analog.png"
        self.instrument_image_label = QLabel()
        self.instrument_icon_folder = "analog_synths"
        self.instrument_image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center align the image
        self.main_window = parent
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        self.presets = ANALOG_PRESETS_ENUMERATED
        self.preset_type = SynthType.ANALOG
        self.midi_requests = [PROGRAM_COMMON_REQUEST, ANALOG_REQUEST]
        self.midi_channel = MIDI_CHANNEL_ANALOG
        # Create scroll area for resizable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # Store parameter controls for easy access
        self.controls: Dict[Union[AnalogParameter], QWidget] = {}
        self.updating_from_spinbox = False
        # Create container widget for scroll area
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)

        # Additional styling specific to analog editor
        self.setStyleSheet(Style.JDXI_TABS_ANALOG + Style.JDXI_EDITOR_ANALOG)
        upper_layout = QHBoxLayout()
        container_layout.addLayout(upper_layout)

        # Title and drum kit selection
        instrument_preset_group = QGroupBox("Analog Synth")
        self.instrument_title_label = QLabel(
            f"Analog Synth:\n {self.presets[0]}" if self.presets else "Analog Synth"
        )
        instrument_preset_group.setStyleSheet(
            """
            QGroupBox {
            width: 100px;
            }
        """
        )
        self.instrument_title_label.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
        """
        )
        instrument_title_group_layout = QVBoxLayout()
        instrument_preset_group.setLayout(instrument_title_group_layout)
        instrument_title_group_layout.addWidget(self.instrument_title_label)

        # Add the "Read Request" button
        self.read_request_button = QPushButton("Send Read Request to Synth")
        self.read_request_button.clicked.connect(self.data_request)
        instrument_title_group_layout.addWidget(self.read_request_button)

        self.instrument_selection_label = QLabel("Select an Analog synth:")
        instrument_title_group_layout.addWidget(self.instrument_selection_label)
        # Synth selection
        self.instrument_selection_combo = PresetComboBox(ANALOG_PRESET_LIST)
        self.instrument_selection_combo.setStyleSheet(Style.JDXI_COMBO_BOX_ANALOG)
        self.instrument_selection_combo.combo_box.setEditable(True)  # Allow text search
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_image
        )
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
        # Add sections side by side
        self.tab_widget = QTabWidget()
        container_layout.addWidget(self.tab_widget)
        self.tab_widget.addTab(
            self._create_oscillator_section(),
            qta.icon("mdi.triangle-wave", color="#666666"),
            "Oscillator",
        )
        self.tab_widget.addTab(
            self._create_filter_section(),
            qta.icon("ri.filter-3-fill", color="#666666"),
            "Filter",
        )
        self.tab_widget.addTab(
            self._create_amp_section(),
            qta.icon("mdi.amplifier", color="#666666"),
            "Amp",
        )
        self.tab_widget.addTab(
            self._create_lfo_section(),
            qta.icon("mdi.sine-wave", color="#666666"),
            "LFO",
        )

        # Add container to scroll area
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # Connect filter controls
        self.filter_resonance.valueChanged.connect(
            lambda v: self.send_control_change(
                AnalogParameter.FILTER_RESONANCE.value[0], v
            )
        )
        self.midi_helper.midi_sysex_json.connect(self._update_sliders_from_sysex)
        for param, slider in self.controls.items():
            if isinstance(slider, QSlider):  # Ensure it's address slider
                slider.setTickPosition(
                    QSlider.TickPosition.TicksBothSides
                )  # Tick marks on both sides
                slider.setTickInterval(10)  # Adjust interval as needed
        self.data_request()
        self.midi_helper.midi_parameter_received.connect(self._on_parameter_received)
        # Initialize previous JSON data storage
        self.previous_json_data = None
        self.refresh_shortcut = QShortcut(QKeySequence.StandardKey.Refresh, self)
        self.refresh_shortcut.activated.connect(self.data_request)
        if self.midi_helper:
            self.midi_helper.midi_program_changed.connect(self._handle_program_change)
            # Register the callback for incoming MIDI messages
            logging.info("MIDI helper initialized")
            if hasattr(self.midi_helper, "set_callback"):
                self.midi_helper.set_callback(self.midi_helper.midi_callback)
                logging.info("MIDI callback set")
            else:
                logging.error("MIDI set_callback method not found")
        else:
            logging.error("MIDI helper not initialized")
        self.midi_helper.update_analog_tone_name.connect(self.set_instrument_title_label)
        self.midi_helper.midi_sysex_json.connect(self._update_sliders_from_sysex)
        self.instrument_selection_combo.preset_loaded.connect(self.load_preset)

    def _create_oscillator_section(self):
        group = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(1, 1, 1, 1)  # Remove margins
        group.setLayout(layout)

        # Waveform buttons
        wave_layout = QHBoxLayout()
        self.wave_buttons = {}
        for waveform in [Waveform.SAW, Waveform.TRIANGLE, Waveform.PULSE]:
            btn = AnalogWaveformButton(waveform)
            btn.setStyleSheet(Style.JDXI_BUTTON_RECT_ANALOG)

            # Set icons for each waveform
            if waveform == Waveform.SAW:
                saw_icon_base64 = generate_waveform_icon("upsaw", "#FFFFFF", 1.0)
                saw_pixmap = base64_to_pixmap(saw_icon_base64)
                btn.setIcon(QIcon(saw_pixmap))
            elif waveform == Waveform.TRIANGLE:
                tri_icon_base64 = generate_waveform_icon("triangle", "#FFFFFF", 1.0)
                tri_pixmap = base64_to_pixmap(tri_icon_base64)
                btn.setIcon(QIcon(tri_pixmap))
            elif waveform == Waveform.PULSE:
                pulse_icon_base64 = generate_waveform_icon("pwsqu", "#FFFFFF", 1.0)
                pulse_pixmap = base64_to_pixmap(pulse_icon_base64)
                btn.setIcon(QIcon(pulse_pixmap))

            btn.waveform_selected.connect(self._on_waveform_selected)
            self.wave_buttons[waveform] = btn
            wave_layout.addWidget(btn)
        layout.addLayout(wave_layout)

        # Tuning controls
        tuning_group = QGroupBox("Tuning")
        tuning_layout = QVBoxLayout()
        tuning_group.setLayout(tuning_layout)

        self.osc_pitch_coarse = self._create_parameter_slider(
            AnalogParameter.OSC_PITCH_COARSE, "Coarse"
        )
        self.osc_pitch_fine = self._create_parameter_slider(
            AnalogParameter.OSC_PITCH_FINE, "Fine"
        )

        tuning_layout.addWidget(self.osc_pitch_coarse)
        tuning_layout.addWidget(self.osc_pitch_fine)
        layout.addWidget(tuning_group)

        # Pulse Width controls
        pw_group = QGroupBox("Pulse Width")
        pw_layout = QVBoxLayout()
        pw_group.setLayout(pw_layout)

        self.osc_pulse_width = self._create_parameter_slider(
            AnalogParameter.OSC_PULSE_WIDTH,
            "Width",
        )
        self.osc_pulse_width_mod_depth = self._create_parameter_slider(
            AnalogParameter.OSC_PULSE_WIDTH_MOD_DEPTH,
            "Mod Depth",
        )

        pw_layout.addWidget(self.osc_pulse_width)
        pw_layout.addWidget(self.osc_pulse_width_mod_depth)
        layout.addWidget(pw_group)

        # Pitch Envelope
        pitch_env_group = QGroupBox("Pitch Envelope")
        pitch_env_layout = QVBoxLayout()
        pitch_env_group.setLayout(pitch_env_layout)

        self.pitch_env_velo = self._create_parameter_slider(
            AnalogParameter.OSC_PITCH_ENV_VELOCITY_SENSITIVITY, "Mod Depth"
        )
        self.pitch_env_attack = self._create_parameter_slider(
            AnalogParameter.OSC_PITCH_ENV_ATTACK_TIME, "Attack"
        )
        self.pitch_env_decay = self._create_parameter_slider(
            AnalogParameter.OSC_PITCH_ENV_DECAY, "Decay"
        )
        self.pitch_env_depth = self._create_parameter_slider(
            AnalogParameter.OSC_PITCH_ENV_DEPTH, "Depth"
        )

        pitch_env_layout.addWidget(self.pitch_env_velo)
        pitch_env_layout.addWidget(self.pitch_env_attack)
        pitch_env_layout.addWidget(self.pitch_env_decay)
        pitch_env_layout.addWidget(self.pitch_env_depth)
        layout.addWidget(pitch_env_group)

        # Sub Oscillator
        sub_group = QGroupBox("Sub Oscillator")
        sub_layout = QVBoxLayout()
        sub_group.setLayout(sub_layout)

        self.sub_oscillator_type_switch = self._create_parameter_switch(AnalogParameter.SUB_OSCILLATOR_TYPE,
            "Type",
            [
                SubOscType.OFF.display_name,
                SubOscType.OCT_DOWN_1.display_name,
                SubOscType.OCT_DOWN_2.display_name,
            ],
        )
        sub_layout.addWidget(self.sub_oscillator_type_switch)
        layout.addWidget(sub_group)

        # Update PW controls enabled state based on current waveform
        self._update_pw_controls_state(Waveform.SAW)  # Initial state

        return group

    def _create_filter_section(self):
        """Create the filter section"""
        filter_group = QWidget()
        filter_group_layout = QVBoxLayout()
        filter_group.setLayout(filter_group_layout)

        # prettify with icons
        adsr_icon_row_layout = QHBoxLayout()
        for icon in [
            "mdi.triangle-wave",
            "mdi.sine-wave",
            "fa5s.wave-square",
            "mdi.cosine-wave",
            "mdi.triangle-wave",
            "mdi.waveform",
        ]:
            adsr_icon_label = QLabel()
            icon = qta.icon(icon, color="#666666")  # Set icon color to grey
            adsr_pixmap = icon.pixmap(30, 30)  # Set the desired size
            adsr_icon_label.setPixmap(adsr_pixmap)
            adsr_icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            adsr_icon_row_layout.addWidget(adsr_icon_label)
        filter_group_layout.addLayout(adsr_icon_row_layout)

        # Filter controls
        self.filter_switch = self._create_parameter_switch(AnalogParameter.FILTER_SWITCH,
                                                           "Filter",
                                                           ["BYPASS", "LPF"])
        filter_group_layout.addWidget(self.filter_switch)
        self.filter_cutoff = self._create_parameter_slider(
            AnalogParameter.FILTER_CUTOFF, "Cutoff"
        )
        self.filter_resonance = self._create_parameter_slider(
            AnalogParameter.FILTER_RESONANCE, "Resonance"
        )
        self.filter_cutoff_keyfollow = self._create_parameter_slider(
            AnalogParameter.FILTER_CUTOFF_KEYFOLLOW, "Keyfollow"
        )
        # Create ADSRWidget
        self.filter_adsr_widget = ADSR(
            AnalogParameter.FILTER_ENV_ATTACK_TIME,
            AnalogParameter.FILTER_ENV_DECAY_TIME,
            AnalogParameter.FILTER_ENV_SUSTAIN_LEVEL,
            AnalogParameter.FILTER_ENV_RELEASE_TIME,
            self.midi_helper,
            area=self.area,
            part=self.part,
            group=self.group
        )
        self.filter_adsr_widget.setStyleSheet(Style.JDXI_ADSR_ANALOG)
        self.filter_env_depth = self._create_parameter_slider(
            AnalogParameter.FILTER_ENV_DEPTH, "Depth"
        )

        self.filter_env_velocity_sens = self._create_parameter_slider(
            AnalogParameter.FILTER_ENV_VELOCITY_SENSITIVITY, "Env. Velocity Sens."
        )
        filter_group_layout.addWidget(self.filter_cutoff)
        filter_group_layout.addWidget(self.filter_resonance)
        filter_group_layout.addWidget(self.filter_cutoff_keyfollow)

        filter_group_layout.addWidget(self.filter_env_depth)
        filter_group_layout.addWidget(self.filter_env_velocity_sens)

        # Add spacing
        filter_group_layout.addSpacing(10)

        # Generate the ADSR waveform icon
        adsr_icon_base64 = generate_waveform_icon("adsr", "#FFFFFF", 2.0)
        adsr_pixmap = base64_to_pixmap(adsr_icon_base64)  # Convert to QPixmap

        # Vbox to vertically arrange icons and ADSR(D) Envelope controls
        sub_layout = QVBoxLayout()

        adsr_icon_label = QLabel()
        adsr_icon_label.setPixmap(adsr_pixmap)
        adsr_icon_label.setAlignment(Qt.AlignHCenter)
        adsr_icon_row_layout = QHBoxLayout()
        adsr_icon_row_layout.addWidget(adsr_icon_label)
        sub_layout.addLayout(adsr_icon_row_layout)

        # Filter envelope
        env_group = QGroupBox("Envelope")
        env_group.setProperty("adsr", True)  # Mark as ADSR area
        envelope_layout = QHBoxLayout()
        env_group.setLayout(envelope_layout)
        envelope_layout.setSpacing(5)
        envelope_layout.addWidget(self.filter_adsr_widget)

        # Generate the ADSR waveform icon
        adsr_icon_base64 = generate_waveform_icon("adsr", "#FFFFFF", 2.0)
        adsr_pixmap = base64_to_pixmap(adsr_icon_base64)  # Convert to QPixmap

        # Vbox to vertically arrange icons and ADSR(D) Envelope controls
        adsr_icon_label = QLabel()
        adsr_icon_label.setPixmap(adsr_pixmap)
        adsr_icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        adsr_icon_row_layout = QHBoxLayout()
        adsr_icon_row_layout.addWidget(adsr_icon_label)
        filter_group_layout.addLayout(adsr_icon_row_layout)
        filter_group_layout.addWidget(env_group)
        filter_group_layout.addStretch()
        return filter_group

    def _create_amp_section(self):
        """Create the Amp section"""
        group = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(5, 15, 5, 5)
        group.setLayout(layout)

        icons_hlayout = QHBoxLayout()
        for icon in [
            "mdi.volume-variant-off",
            "mdi6.volume-minus",
            "mdi.amplifier",
            "mdi6.volume-plus",
            "mdi.waveform",
        ]:
            icon_label = QLabel()
            icon = qta.icon(icon, color="#666666")  # Set icon color to grey
            pixmap = icon.pixmap(
                Style.ICON_SIZE, Style.ICON_SIZE
            )  # Set the desired size
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            icons_hlayout.addWidget(icon_label)
        layout.addLayout(icons_hlayout)

        # Level control
        self.amp_level = self._create_parameter_slider(
            AnalogParameter.AMP_LEVEL, "Level"
        )
        self.amp_level_keyfollow = self._create_parameter_slider(
            AnalogParameter.AMP_LEVEL_KEYFOLLOW, "Keyfollow"
        )
        layout.addWidget(self.amp_level)
        layout.addWidget(self.amp_level_keyfollow)

        # Add spacing
        layout.addSpacing(10)

        # Amp envelope
        env_group = QGroupBox("Envelope")
        env_group.setProperty("adsr", True)  # Mark as ADSR area
        # env_group.setMaximumHeight(300)
        amp_env_adsr_vlayout = QVBoxLayout()
        env_layout = QHBoxLayout()
        env_layout.setSpacing(5)
        env_layout.setContentsMargins(5, 15, 5, 5)
        env_group.setLayout(amp_env_adsr_vlayout)

        # Generate the ADSR waveform icon
        icon_base64 = generate_waveform_icon("adsr", "#FFFFFF", 2.0)
        pixmap = base64_to_pixmap(icon_base64)  # Convert to QPixmap

        # Vbox to vertically arrange icons and ADSR(D) Envelope controls
        sub_layout = QVBoxLayout()

        icon_label = QLabel()
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        icons_hlayout = QHBoxLayout()
        icons_hlayout.addWidget(icon_label)
        sub_layout.addLayout(icons_hlayout)
        self.amp_env_adsr_widget = ADSR(
            AnalogParameter.AMP_ENV_ATTACK_TIME,
            AnalogParameter.AMP_ENV_DECAY_TIME,
            AnalogParameter.AMP_ENV_SUSTAIN_LEVEL,
            AnalogParameter.AMP_ENV_RELEASE_TIME,
            self.midi_helper,
            area=self.area,
            part=self.part,
            group=self.group
        )
        self.amp_env_adsr_widget.setStyleSheet(Style.JDXI_ADSR_ANALOG)
        amp_env_adsr_vlayout.addWidget(self.amp_env_adsr_widget)
        sub_layout.addWidget(env_group)
        sub_layout.addStretch()
        layout.addLayout(sub_layout)
        return group

    def _create_lfo_section(self):
        """Create the LFO section"""
        group = QWidget()
        layout = QVBoxLayout()
        group.setLayout(layout)

        # Replace the LFO Shape selector combo box with buttons
        shape_row = QHBoxLayout()
        shape_row.addWidget(QLabel("Shape"))
        shape_row.addStretch(1)  # Add stretch before buttons
        self.lfo_shape_buttons = {}

        # Create buttons for each LFO shape
        lfo_shapes = [
            ("TRI", "mdi.triangle-wave", 0),
            ("SIN", "mdi.sine-wave", 1),
            ("SAW", "mdi.sawtooth-wave", 2),
            ("SQR", "mdi.square-wave", 3),
            ("S&H", "mdi.waveform", 4),  # Sample & Hold
            ("RND", "mdi.wave", 5),  # Random
        ]

        for name, icon_name, value in lfo_shapes:
            btn = QPushButton(name)  # Add text to button
            btn.setCheckable(True)
            btn.setProperty("value", value)
            icon = qta.icon(icon_name)
            btn.setIcon(icon)
            btn.setIconSize(QSize(24, 24))
            btn.setFixedSize(80, 40)  # Make buttons wider to accommodate text
            btn.setToolTip(name)
            btn.clicked.connect(lambda checked, v=value: self._on_lfo_shape_changed(v))
            btn.setStyleSheet(Style.JDXI_BUTTON_RECT_ANALOG)
            self.lfo_shape_buttons[value] = btn
            shape_row.addWidget(btn)
            shape_row.addStretch(1)  # Add stretch after each button

        layout.addLayout(shape_row)

        # Rate and Fade Time
        self.lfo_rate = self._create_parameter_slider(AnalogParameter.LFO_RATE, "Rate")

        self.lfo_fade = self._create_parameter_slider(
            AnalogParameter.LFO_FADE_TIME, "Fade Time"
        )

        # Tempo Sync controls
        sync_row = QHBoxLayout()
        self.lfo_sync_switch = self._create_parameter_switch(AnalogParameter.LFO_TEMPO_SYNC_SWITCH,
                                                             "Tempo Sync",
                                                             ["OFF", "ON"])
        sync_row.addWidget(self.lfo_sync_switch)

        self.lfo_sync_note_label = QLabel("Sync note")
        self.lfo_sync_note = self._create_parameter_combo_box(
            AnalogParameter.LFO_TEMPO_SYNC_NOTE, "", options=LFO_TEMPO_SYNC_NOTES, show_label=False
        )
        sync_row.addWidget(self.lfo_sync_note_label)
        sync_row.addWidget(self.lfo_sync_note)

        # Depth controls
        self.lfo_pitch = self._create_parameter_slider(
            AnalogParameter.LFO_PITCH_DEPTH, "Pitch Depth"
        )

        self.lfo_filter = self._create_parameter_slider(
            AnalogParameter.LFO_FILTER_DEPTH,
            "Filter Depth",
        )

        self.lfo_amp = self._create_parameter_slider(
            AnalogParameter.LFO_AMP_DEPTH, "Amp Depth"
        )

        # Key Trigger switch
        self.key_trigger_switch = self._create_parameter_switch(AnalogParameter.LFO_KEY_TRIGGER,
                                                                "Key Trigger",
                                                                ["OFF", "ON"])

        # Add all controls to layout
        layout.addWidget(self.lfo_rate)
        layout.addWidget(self.lfo_fade)
        layout.addLayout(sync_row)
        layout.addWidget(self.lfo_pitch)
        layout.addWidget(self.lfo_filter)
        layout.addWidget(self.lfo_amp)
        layout.addWidget(self.key_trigger_switch)

        return group

    def _on_parameter_received(self, address, value):
        """Handle parameter updates from MIDI messages."""
        area_code = address[0]
        if address[0] == TEMPORARY_ANALOG_SYNTH_AREA:
            # Extract the actual parameter address (80, 0) from [25, 1, 80, 0]
            parameter_address = tuple(address[2:])  # (80, 0)

            # Retrieve the corresponding DigitalParameter
            param = get_analog_parameter_by_address(parameter_address)
            partial_no = address[1]
            if param:
                logging.info(f"param: \t{param} \taddress=\t{address}, Value=\t{value}")

                # Update the corresponding slider
                if param in self.controls:
                    slider_value = param.convert_from_midi(value)
                    logging.info(
                        f"midi value {value} converted to slider value {slider_value}"
                    )
                    slider = self.controls[param]
                    slider.blockSignals(True)  # Prevent feedback loop
                    slider.setValue(slider_value)
                    slider.blockSignals(False)

                # Handle OSC_WAVE parameter to update waveform buttons
                if param == AnalogParameter.OSC_WAVEFORM:
                    self._update_waveform_buttons(value)
                    logging.debug(
                        "updating waveform buttons for param {param} with {value}"
                    )

    def _on_waveform_selected(self, waveform: Waveform):
        """Handle waveform button selection KEEP!"""
        if self.midi_helper:
            sysex_message = RolandSysEx(area=self.area,
                                        section=self.part,
                                        group=self.group,
                                        param=AnalogParameter.OSC_WAVEFORM.value[0],
                                        value=waveform.midi_value)
            self.midi_helper.send_midi_message(sysex_message)

            for btn in self.wave_buttons.values():
                btn.setChecked(False)
                btn.setStyleSheet(Style.JDXI_BUTTON_RECT_ANALOG)

            # Apply active style to the selected waveform button
            selected_btn = self.wave_buttons.get(waveform)
            if selected_btn:
                selected_btn.setChecked(True)
                selected_btn.setStyleSheet(Style.JDXI_BUTTON_ANALOG_ACTIVE)
            self._update_pw_controls_state(waveform)

    def _on_lfo_shape_changed(self, value: int):
        """Handle LFO shape change"""
        if self.midi_helper:
            sysex_message = RolandSysEx(area=self.area,
                                        section=self.part,
                                        group=self.group,
                                        param=AnalogParameter.LFO_SHAPE.value[0],
                                        value=value)
            self.midi_helper.send_midi_message(sysex_message)
            # Reset all buttons to default style
            for btn in self.lfo_shape_buttons.values():
                btn.setChecked(False)
                btn.setStyleSheet(Style.JDXI_BUTTON_RECT_ANALOG)

            # Apply active style to the selected button
            selected_btn = self.lfo_shape_buttons.get(value)
            if selected_btn:
                selected_btn.setChecked(True)
                selected_btn.setStyleSheet(Style.JDXI_BUTTON_ANALOG_ACTIVE)

    def _update_sliders_from_sysex(self, json_sysex_data: str):
        """Update sliders and combo boxes based on parsed SysEx data."""
        logging.info("Updating UI components from SysEx data")

        try:
            current_sysex_data = json.loads(json_sysex_data)
        except json.JSONDecodeError as ex:
            logging.error(f"Invalid JSON format: {ex}")
            return

        # Compare with previous data and log changes
        if self.previous_json_data:
            _log_changes(self.previous_json_data, current_sysex_data)

        # Store the current data for future comparison
        self.previous_json_data = current_sysex_data

        if current_sysex_data.get("TEMPORARY_AREA") != "TEMPORARY_ANALOG_SYNTH_AREA":
            logging.warning(
                "SysEx data does not belong to TEMPORARY_ANALOG_SYNTH_AREA. Skipping update."
            )
            return

        # Remove unnecessary keys
        ignored_keys = {
            "JD_XI_HEADER",
            "ADDRESS",
            "TEMPORARY_AREA",
            "TONE_NAME",
            "SYNTH_TONE",
        }
        current_sysex_data = {
            k: v for k, v in current_sysex_data.items() if k not in ignored_keys
        }

        # Define mapping dictionaries
        sub_osc_type_map = {0: 0, 1: 1, 2: 2}
        filter_switch_map = {0: 0, 1: 1}
        osc_waveform_map = {0: Waveform.SAW, 1: Waveform.TRIANGLE, 2: Waveform.PULSE}

        failures, successes = [], []

        def update_slider(param, value):
            """Helper function to update sliders safely."""
            slider = self.controls.get(param)
            if slider:
                slider_value = param.convert_from_midi(value)
                slider.blockSignals(True)
                slider.setValue(slider_value)
                slider.blockSignals(False)
                successes.append(param.name)

        def update_adsr_widget(param, value):
            """Helper function to update ADSR widgets."""
            new_value = (
                midi_cc_to_frac(value)
                if param
                   in [
                       AnalogParameter.AMP_ENV_SUSTAIN_LEVEL,
                       AnalogParameter.FILTER_ENV_SUSTAIN_LEVEL,
                   ]
                else midi_cc_to_ms(value)
            )

            adsr_mapping = {
                AnalogParameter.AMP_ENV_ATTACK_TIME: self.amp_env_adsr_widget.attack_sb,
                AnalogParameter.AMP_ENV_DECAY_TIME: self.amp_env_adsr_widget.decay_sb,
                AnalogParameter.AMP_ENV_SUSTAIN_LEVEL: self.amp_env_adsr_widget.sustain_sb,
                AnalogParameter.AMP_ENV_RELEASE_TIME: self.amp_env_adsr_widget.release_sb,
                AnalogParameter.FILTER_ENV_ATTACK_TIME: self.filter_adsr_widget.attack_sb,
                AnalogParameter.FILTER_ENV_DECAY_TIME: self.filter_adsr_widget.decay_sb,
                AnalogParameter.FILTER_ENV_SUSTAIN_LEVEL: self.filter_adsr_widget.sustain_sb,
                AnalogParameter.FILTER_ENV_RELEASE_TIME: self.filter_adsr_widget.release_sb,
            }

            if param in adsr_mapping:
                spinbox = adsr_mapping[param]
                spinbox.setValue(new_value)

        for param_name, param_value in current_sysex_data.items():
            param = AnalogParameter.get_by_name(param_name)

            if param: # @@
                if param_name in ["LFO_SHAPE", "LFO_PITCH_DEPTH", "LFO_FILTER_DEPTH", "LFO_AMP_DEPTH", "PULSE_WIDTH"]:
                    nrpn_map = {
                        (0, 124): "Envelope",
                        (0, 3): "LFO Shape",
                        (0, 15): "LFO Pitch Depth",
                        (0, 18): "LFO Filter Depth",
                        (0, 21): "LFO Amp Depth",
                        (0, 37): "Pulse Width",
                    }
                    nrpn_address = next(
                        (addr for addr, name in nrpn_map.items() if name == param_name), None
                    )
                    if nrpn_address:
                        self._handle_nrpn_message(nrpn_address, param_value, channel=1)
                elif param_name == "LFO_SHAPE" and param_value in self.lfo_shape_buttons:
                    self._update_lfo_shape_buttons(param_value)
                elif (
                        param_name == "SUB_OSCILLATOR_TYPE"
                        and param_value in sub_osc_type_map
                ):
                    self.sub_oscillator_type_switch.blockSignals(True)
                    self.sub_oscillator_type_switch.setValue(sub_osc_type_map[param_value])
                    self.sub_oscillator_type_switch.blockSignals(False)
                elif param_name == "OSC_WAVEFORM" and param_value in osc_waveform_map:
                    self._update_waveform_buttons(param_value)
                elif param_name == "FILTER_SWITCH" and param_value in filter_switch_map:
                    self.filter_switch.blockSignals(True)
                    self.filter_switch.setValue(filter_switch_map[param_value])
                    self.filter_switch.blockSignals(False)
                else:
                    update_slider(param, param_value)
                    update_adsr_widget(param, param_value)
            else:
                failures.append(param_name)

        logging.info(f"Updated {len(successes)} parameters successfully.")
        if failures:
            logging.warning(f"Failed to update {len(failures)} parameters: {failures}")

    def _update_waveform_buttons(self, value):
        """Update the waveform buttons based on the OSC_WAVE value with visual feedback."""
        logging.debug(f"Updating waveform buttons with value {value}")

        waveform_map = {
            0: Waveform.SAW,
            1: Waveform.TRIANGLE,
            2: Waveform.PULSE,
        }

        selected_waveform = waveform_map.get(value)

        if selected_waveform is None:
            logging.warning(f"Unknown waveform value: {value}")
            return

        logging.debug(f"Waveform value {value} found, selecting {selected_waveform}")

        # Retrieve waveform buttons for the given partial
        wave_buttons = self.wave_buttons

        # Reset all buttons to default style
        for btn in wave_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(Style.JDXI_BUTTON_RECT_ANALOG)

        # Apply active style to the selected waveform button
        selected_btn = wave_buttons.get(selected_waveform)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(Style.JDXI_BUTTON_ANALOG_ACTIVE)

    def _update_lfo_shape_buttons(self, value):
        """Update the LFO shape buttons with visual feedback."""
        logging.debug(f"Updating LFO shape buttons with value {value}")

        # Reset all buttons to default style
        for btn in self.lfo_shape_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(Style.JDXI_BUTTON_RECT_ANALOG)

        # Apply active style to the selected button
        selected_btn = self.lfo_shape_buttons.get(value)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(Style.JDXI_BUTTON_ANALOG_ACTIVE)
        else:
            logging.warning(f"Unknown LFO shape value: {value}")

    def _update_pw_controls_state(self, waveform: Waveform):
        """Enable/disable PW controls based on waveform"""
        pw_enabled = waveform == Waveform.PULSE
        self.osc_pulse_width.setEnabled(pw_enabled)
        self.osc_pulse_width_mod_depth.setEnabled(pw_enabled)
        # Update the visual state
        self.osc_pulse_width.setStyleSheet(
            "" if pw_enabled else "QSlider::groove:vertical { background: #000000; }"
        )
        self.osc_pulse_width_mod_depth.setStyleSheet(
            "" if pw_enabled else "QSlider::groove:vertical { background: #000000; }"
        )
