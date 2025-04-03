"""
Digital Partial Editor Module

This module defines the `DigitalPartialEditor` class, a specialized editor for managing a single
digital partial in a synthesizer. It extends the `PartialEditor` class, providing a structured UI
to control and modify parameters related to oscillators, filters, amplifiers, and modulation sources.

Classes:
    - DigitalPartialEditor: A `QWidget` subclass that allows users to modify digital synthesis
      parameters using a tabbed interface with various control sections.

Features:
    - Supports editing a single partial within a digital synth part.
    - Provides categorized parameter sections: Oscillator, Filter, Amp, LFO, and Mod LFO.
    - Integrates with `MIDIHelper` for real-time MIDI parameter updates.
    - Uses icons for waveform selection, filter controls, and modulation settings.
    - Stores UI controls for easy access and interaction.

Usage:
    ```python
    from PySide6.QtWidgets import QApplication
    from midi_helper import MIDIHelper

    app = QApplication([])
    midi_helper = MIDIHelper()
    editor = DigitalPartialEditor(midi_helper=midi_helper)
    editor.show()
    app.exec()
    ```

Dependencies:
    - PySide6 (for UI components)
    - MIDIHelper (for MIDI communication)
    - DigitalParameter, DigitalCommonParameter (for parameter management)
    - WaveformButton (for waveform selection UI)
    - QIcons generated from waveform base64 data
"""

import logging
from typing import Dict, Union

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QTabWidget, QGridLayout, QFormLayout, QComboBox,
)

from jdxi_editor.midi.data.digital.lfo import DigitalLFOShape, DigitalLFOTempoSyncNote
from jdxi_editor.midi.data.lfo.lfo import LFOSyncNote
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParameter
from jdxi_editor.midi.data.digital import DigitalOscWave, DIGITAL_PARTIAL_NAMES
from jdxi_editor.midi.data.parameter.digital.common import DigitalCommonParameter
from jdxi_editor.midi.data.constants.sysex import DIGITAL_SYNTH_1_AREA, DIGITAL_SYNTH_2_AREA, \
    DIGITAL_PART_1, DIGITAL_PART_2
from jdxi_editor.midi.data.presets.pcm_waves import PCM_WAVES, PCM_WAVES_CATEGORIZED
from jdxi_editor.midi.sysex.parsers import get_partial_address
from jdxi_editor.midi.utils.conversions import (
    midi_cc_to_frac,
    midi_cc_to_ms,
    ms_to_midi_cc,
)
from jdxi_editor.ui.editors.synth.partial import PartialEditor
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.style import Style
# from jdxi_editor.ui.widgets.adsr.pitch_envelope import PitchEnvelope
from jdxi_editor.ui.widgets.button.waveform import WaveformButton
from jdxi_editor.ui.widgets.adsr.adsr import ADSR
from jdxi_editor.ui.widgets.switch.switch import Switch
from jdxi_editor.ui.image.waveform import (
    generate_waveform_icon,
)


class DigitalPartialEditor(PartialEditor):
    """Editor for address single partial"""

    def __init__(self, midi_helper=None, partial_number=1, parent=None):
        super().__init__(parent)
        self.bipolar_parameters = [
            DigitalPartialParameter.OSC_DETUNE,
            DigitalPartialParameter.OSC_PITCH,
            DigitalPartialParameter.OSC_PITCH_ENV_DEPTH,
            DigitalPartialParameter.AMP_PAN,
        ]
        self.midi_helper = midi_helper
        self.partial_number = partial_number
        self.area = DIGITAL_SYNTH_1_AREA if partial_number == 1 else DIGITAL_SYNTH_2_AREA
        self.part = DIGITAL_PART_1 if partial_number == 1 else DIGITAL_PART_2
        # self.part = part
        if 0 <= partial_number < len(DIGITAL_PARTIAL_NAMES):
            self.part_name = DIGITAL_PARTIAL_NAMES[partial_number]
        else:
            logging.error(f"Invalid partial_num: {partial_number}. Using default value.")
            self.part_name = "Unknown"  # Provide a fallback value
        try:
            self.group = get_partial_address(self.part_name)
        except Exception as e:
            logging.error(f"Failed to get partial address for {self.part_name}: {e}")
            self.group = 0x00  # Provide a default address

        # Store parameter controls for easy access
        self.controls: Dict[
            Union[DigitalPartialParameter, DigitalCommonParameter], QWidget
        ] = {}

        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Create container widget for the tabs
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        self.tab_widget = QTabWidget()
        container_layout.addWidget(self.tab_widget)
        # Add sections in address vertical layout
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
        self.tab_widget.addTab(
            self._create_mod_lfo_section(),
            qta.icon("mdi.waveform", color="#666666"),
            "Mod LFO",
        )

        # Add container to scroll area
        main_layout.addWidget(container)
        self.updating_from_spinbox = False

    def _create_oscillator_section(self):
        """Create the oscillator section of the partial editor"""
        oscillator_section = QWidget()
        layout = QVBoxLayout()
        oscillator_section.setLayout(layout)

        # Top row: Waveform buttons and variation
        top_row = QHBoxLayout()

        # Waveform buttons
        wave_layout = QHBoxLayout()
        self.wave_buttons = {}

        wave_icons = {
            DigitalOscWave.SAW: generate_waveform_icon("upsaw", "#FFFFFF", 1.0),
            DigitalOscWave.SQUARE: generate_waveform_icon("square", "#FFFFFF", 1.0),
            DigitalOscWave.PW_SQUARE: generate_waveform_icon("pwsqu", "#FFFFFF", 1.0),
            DigitalOscWave.TRIANGLE: generate_waveform_icon("triangle", "#FFFFFF", 1.0),
            DigitalOscWave.SINE: generate_waveform_icon("sine", "#FFFFFF", 1.0),
            DigitalOscWave.NOISE: generate_waveform_icon("noise", "#FFFFFF", 1.0),
            DigitalOscWave.SUPER_SAW: generate_waveform_icon("spsaw", "#FFFFFF", 1.0),
            DigitalOscWave.PCM: generate_waveform_icon("pcm", "#FFFFFF", 1.0),
        }

        for wave, icon_base64 in wave_icons.items():
            btn = WaveformButton(wave)
            btn.setStyleSheet(Style.JDXI_BUTTON_RECT)  # Apply default styles
            btn.setFixedSize(60, 30)
            # Set waveform icons
            wave_pixmap = base64_to_pixmap(icon_base64)
            btn.setIcon(QIcon(wave_pixmap))

            # Connect click signal
            btn.clicked.connect(lambda checked, w=wave: self._on_waveform_selected(w))

            self.wave_buttons[wave] = btn
            wave_layout.addWidget(btn)

        top_row.addLayout(wave_layout)

        # Wave variation switch
        self.wave_variation_switch = self._create_parameter_switch(DigitalPartialParameter.OSC_WAVE_VARIATION,
                                                                   "Variation",
                                                                   ["A", "B", "C"])
        top_row.addWidget(self.wave_variation_switch)
        layout.addLayout(top_row)

        # Tuning controls
        tuning_group = QGroupBox("Tuning")
        tuning_layout = QVBoxLayout()
        tuning_group.setLayout(tuning_layout)

        tuning_layout.addWidget(
            self._create_parameter_slider(DigitalPartialParameter.OSC_PITCH, "Pitch")
        )
        tuning_layout.addWidget(
            self._create_parameter_slider(DigitalPartialParameter.OSC_DETUNE, "Detune")
        )
        layout.addWidget(tuning_group)

        # Pulse Width controls (only enabled for PW-SQUARE wave)
        pw_group = QGroupBox("Pulse Width")
        pw_layout = QVBoxLayout()
        pw_group.setLayout(pw_layout)

        self.pw_slider = self._create_parameter_slider(
            DigitalPartialParameter.OSC_PULSE_WIDTH, "Width"
        )
        self.pwm_slider = self._create_parameter_slider(
            DigitalPartialParameter.OSC_PULSE_WIDTH_MOD_DEPTH, "Mod"
        )
        pw_layout.addWidget(self.pw_slider)
        pw_layout.addWidget(self.pwm_slider)
        layout.addWidget(pw_group)

        # PCM Wave controls
        pcm_group = QGroupBox("PCM Wave")
        pcm_layout = QGridLayout()
        pcm_group.setLayout(pcm_layout)
        self.pcm_group = pcm_group  # Store reference for visibility control
        self.pcm_wave_gain = self._create_parameter_combo_box(
            DigitalPartialParameter.PCM_WAVE_GAIN, "Gain [dB]", ["-6", "0", "+6", "+12"]
        )
        self.pcm_wave_number = self._create_parameter_combo_box(
            DigitalPartialParameter.PCM_WAVE_NUMBER, "Number", set(w["Wave Number"] for w in PCM_WAVES_CATEGORIZED)
        )

        # Create ComboBoxes
        self.pcm_category_combo = QComboBox()

        # Populate categories (with "No selection" option)
        self.pcm_categories = ["No selection"] + sorted(set(w["Category"] for w in PCM_WAVES_CATEGORIZED))
        self.pcm_category_combo.addItems(self.pcm_categories)

        # Connect signal to update waves
        self.pcm_category_combo.currentIndexChanged.connect(self.update_waves)

        pcm_layout.addWidget(self.pcm_wave_gain, 0, 0)
        pcm_layout.addWidget(QLabel("Category"), 0, 1)
        pcm_layout.addWidget(self.pcm_category_combo, 0, 2)
        pcm_layout.addWidget(self.pcm_wave_number, 0, 3)

        self.update_waves()

        # Add widgets
        layout.addWidget(pcm_group)

        # Pitch Envelope
        pitch_env_group = QGroupBox("Pitch Envelope")
        pitch_env_layout = QVBoxLayout()
        pitch_env_group.setLayout(pitch_env_layout)
        pitch_env_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParameter.OSC_PITCH_ENV_ATTACK_TIME, "Attack"
            )
        )
        pitch_env_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParameter.OSC_PITCH_ENV_DECAY_TIME, "Decay"
            )
        )
        pitch_env_layout.addWidget(
            self._create_parameter_slider(DigitalPartialParameter.OSC_PITCH_ENV_DEPTH, "Depth")
        )

        layout.addWidget(pitch_env_group)

        # Super Saw detune (only for SUPER-SAW wave)
        self.super_saw_detune = self._create_parameter_slider(
            DigitalPartialParameter.SUPER_SAW_DETUNE, "S-Saw Detune"
        )
        layout.addWidget(self.super_saw_detune)

        # Update PW controls enabled state when waveform changes
        self._update_pw_controls_state(DigitalOscWave.SAW)  # Initial state
        self._update_pcm_controls_state(DigitalOscWave.PCM)  # Initial state

        return oscillator_section

    def update_waves(self):
        selected_category = self.pcm_category_combo.currentText()

        # Filter waves or show all if "No selection"
        if selected_category == "No selection":
            filtered_waves = PCM_WAVES_CATEGORIZED  # Show all waves
        else:
            filtered_waves = [w for w in PCM_WAVES_CATEGORIZED if w["Category"] == selected_category]

        # Update wave combo box
        self.pcm_wave_number.combo_box.clear()
        self.pcm_wave_number.combo_box.addItems([f"{w['Wave Number']}: {w['Wave Name']}" for w in filtered_waves])
        self.pcm_wave_number.values = [w["Wave Number"] for w in filtered_waves]

    def _update_pw_controls_state(self, waveform: DigitalOscWave):
        """Update pulse width controls enabled state based on waveform"""
        pw_enabled = waveform == DigitalOscWave.PW_SQUARE
        self.pw_slider.setEnabled(pw_enabled)
        self.pwm_slider.setEnabled(pw_enabled)

    def _update_pcm_controls_state(self, waveform: DigitalOscWave):
        """Update PCM wave controls visibility based on waveform"""
        pcm_enabled = waveform == DigitalOscWave.PCM
        self.pcm_wave_gain.setEnabled(pcm_enabled)
        self.pcm_category_combo.setEnabled(pcm_enabled)
        self.pcm_wave_number.setEnabled(pcm_enabled)

    def _create_filter_section(self):
        """Create the filter section of the partial editor"""
        filter_section = QWidget()
        filter_layout = QVBoxLayout()
        filter_section.setLayout(filter_layout)

        # prettify with icons
        icon_hlayout = QHBoxLayout()
        for icon in ["mdi.sine-wave", "ri.filter-3-fill", "mdi.waveform"]:
            icon_label = QLabel()
            icon = qta.icon(icon, color="#666666")  # Set icon color to grey
            pixmap = icon.pixmap(30, 30)  # Set the desired size
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            icon_hlayout.addWidget(icon_label)
        filter_layout.addLayout(icon_hlayout)

        # Filter preset_type controls
        type_row = QHBoxLayout()

        # Filter mode switch
        self.filter_mode_switch = self._create_parameter_switch(DigitalPartialParameter.FILTER_MODE_SWITCH,
                                                                "Mode",
                                                                ["BYPASS", "LPF", "HPF", "BPF", "PKG", "LPF2", "LPF3",
                                                                 "LPF4"]
                                                                )
        self.filter_mode_switch.valueChanged.connect(lambda v: self._on_filter_mode_changed(v))
        type_row.addWidget(self.filter_mode_switch)

        # Filter slope switch
        self.filter_slope_switch = self._create_parameter_switch(DigitalPartialParameter.FILTER_SLOPE,
                                                                 "Slope",
                                                                 ["-12dB", "-24dB"])
        self.filter_slope_switch = Switch("Slope", ["-12dB", "-24dB"])
        type_row.addWidget(self.filter_slope_switch)
        filter_layout.addLayout(type_row)

        # Main filter controls
        controls_group_box = QGroupBox("Controls")
        controls_layout = QVBoxLayout()
        controls_group_box.setLayout(controls_layout)

        controls_layout.addWidget(
            self._create_parameter_slider(DigitalPartialParameter.FILTER_CUTOFF, "Cutoff")
        )
        controls_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParameter.FILTER_RESONANCE, "Resonance"
            )
        )
        controls_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParameter.FILTER_CUTOFF_KEYFOLLOW, "KeyFollow"
            )
        )
        controls_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParameter.FILTER_ENV_VELOCITY_SENSITIVITY, "Velocity"
            )
        )
        filter_layout.addWidget(controls_group_box)

        # Filter envelope
        env_group = QGroupBox("Envelope")
        env_group.setProperty("adsr", True)  # Mark as ADSR area
        env_layout = QVBoxLayout()
        env_group.setLayout(env_layout)

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

        # Create ADSRWidget
        # self.filter_adsr_widget = ADSRWidget()
        group_address, param_address = (
            DigitalPartialParameter.AMP_ENV_ATTACK_TIME.get_address_for_partial(
                self.partial_number
            )
        )
        self.filter_adsr_widget = ADSR(
            DigitalPartialParameter.FILTER_ENV_ATTACK_TIME,
            DigitalPartialParameter.FILTER_ENV_DECAY_TIME,
            DigitalPartialParameter.FILTER_ENV_SUSTAIN_LEVEL,
            DigitalPartialParameter.FILTER_ENV_RELEASE_TIME,
            self.midi_helper,
            area=DIGITAL_SYNTH_1_AREA,
            part=self.part,
            group=group_address,
            # depth_param=DigitalParameter.FILTER_ENV_DEPTH,
        )
        self.filter_adsr_widget.setStyleSheet(Style.JDXI_ADSR)

        adsr_vlayout = QVBoxLayout()
        env_layout.addWidget(self.filter_adsr_widget)
        # adsr_vlayout.addWidget(self.filter_adsr_widget)
        env_layout.setStretchFactor(self.filter_adsr_widget, 5)

        # ADSR controls
        adsr_layout = QHBoxLayout()
        adsr_vlayout.addLayout(adsr_layout)
        env_layout.addLayout(adsr_vlayout)

        # Envelope depth
        env_layout.addWidget(
            self._create_parameter_slider(DigitalPartialParameter.FILTER_ENV_DEPTH, "Depth")
        )
        sub_layout.addWidget(env_group)
        filter_layout.addLayout(sub_layout)
        env_group.setStyleSheet("QGroupBox { margin-top: 10px; }")
        self.filter_adsr_widget.updateGeometry()
        env_group.updateGeometry()
        return filter_section

    def _on_filter_mode_changed(self, mode: int):
        """Handle filter mode changes"""
        # Update control states
        self.update_filter_controls_state(mode)

    def update_filter_controls_state(self, mode: int):
        """Update filter controls enabled state based on mode"""
        enabled = mode != 0  # Enable if not BYPASS
        for param in [
            DigitalPartialParameter.FILTER_CUTOFF,
            DigitalPartialParameter.FILTER_RESONANCE,
            DigitalPartialParameter.FILTER_CUTOFF_KEYFOLLOW,
            DigitalPartialParameter.FILTER_ENV_VELOCITY_SENSITIVITY,
            DigitalPartialParameter.FILTER_ENV_DEPTH,
            DigitalPartialParameter.FILTER_SLOPE,
        ]:
            if param in self.controls:
                self.controls[param].setEnabled(enabled)
            self.filter_adsr_widget.setEnabled(enabled)

    def _create_amp_section(self):
        """Create the amplifier section of the partial editor"""
        amp_section = QWidget()
        amp_section_layout = QVBoxLayout()
        amp_section.setLayout(amp_section_layout)

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
        amp_section_layout.addLayout(icons_hlayout)

        # Level and velocity controls
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout()
        controls_group.setLayout(controls_layout)

        controls_layout.addWidget(
            self._create_parameter_slider(DigitalPartialParameter.AMP_LEVEL, "Level")
        )
        controls_layout.addWidget(
            self._create_parameter_slider(DigitalPartialParameter.AMP_VELOCITY, "Velocity")
        )

        # Create and center the pan slider
        pan_slider = self._create_parameter_slider(DigitalPartialParameter.AMP_PAN, "Pan")
        pan_slider.setValue(0)  # Center the pan slider
        controls_layout.addWidget(pan_slider)

        amp_section_layout.addWidget(controls_group)

        # Amp envelope
        env_group = QGroupBox("Envelope")
        env_group.setProperty("adsr", True)  # Mark as ADSR area
        env_layout = QHBoxLayout()
        amp_env_adsr_vlayout = QVBoxLayout()
        env_group.setLayout(amp_env_adsr_vlayout)

        # Generate the ADSR waveform icon
        icon_base64 = generate_waveform_icon("adsr", "#FFFFFF", 2.0)
        pixmap = base64_to_pixmap(icon_base64)  # Convert to QPixmap

        icon_label = QLabel()
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        icons_hlayout = QHBoxLayout()
        icons_hlayout.addWidget(icon_label)
        amp_section_layout.addLayout(icons_hlayout)

        # Create ADSRWidget
        group_address, param_address = (
            DigitalPartialParameter.AMP_ENV_ATTACK_TIME.get_address_for_partial(
                self.partial_number
            )
        )
        self.amp_env_adsr_widget = ADSR(
            DigitalPartialParameter.AMP_ENV_ATTACK_TIME,
            DigitalPartialParameter.AMP_ENV_DECAY_TIME,
            DigitalPartialParameter.AMP_ENV_SUSTAIN_LEVEL,
            DigitalPartialParameter.AMP_ENV_RELEASE_TIME,
            self.midi_helper,
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
            self._create_parameter_slider(DigitalPartialParameter.LEVEL_AFTERTOUCH, "AT Sens")
        )
        return amp_section

    def _create_lfo_section(self):
        """Create the LFO section of the partial editor"""
        lfo_section = QWidget()
        layout = QVBoxLayout()
        lfo_section.setLayout(layout)

        icons_hlayout = QHBoxLayout()
        for icon in [
            "mdi.triangle-wave",
            "mdi.sine-wave",
            "fa5s.wave-square",
            "mdi.cosine-wave",
            "mdi.triangle-wave",
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

        # Shape and sync controls
        top_row = QHBoxLayout()

        # Shape switch
        self.lfo_shape = self._create_parameter_switch(DigitalPartialParameter.LFO_SHAPE,
                                                       "Shape",
                                                       ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"])
        top_row.addWidget(self.lfo_shape)

        # Sync switch
        self.lfo_tempo_sync_switch = self._create_parameter_switch(DigitalPartialParameter.LFO_TEMPO_SYNC_SWITCH,
                                                             "Tempo Sync",
                                                            ["OFF", "ON"])
        top_row.addWidget(self.lfo_tempo_sync_switch)
        layout.addLayout(top_row)

        # Rate and fade controls
        layout.addWidget(
            self._create_parameter_slider(DigitalPartialParameter.LFO_RATE,
                                          "Rate")
        )
        layout.addWidget(
            self._create_parameter_slider(DigitalPartialParameter.LFO_FADE_TIME,
                                          "Fade")
        )

        # Key trigger switch
        self.lfo_trigger = self._create_parameter_switch(DigitalPartialParameter.LFO_KEY_TRIGGER,
                                                         "Key Trigger",
                                                         ["OFF", "ON"])
        layout.addWidget(self.lfo_trigger)

        # Modulation depths
        depths_group = QGroupBox("Depths")
        depths_layout = QVBoxLayout()

        # Ensure `depths_group` layout is only set once
        if (
                not depths_group.layout()
        ):  # Check if the area already has address layout assigned
            depths_group.setLayout(depths_layout)

        depths_layout.addWidget(
            self._create_parameter_slider(DigitalPartialParameter.LFO_PITCH_DEPTH,
                                          "Pitch")
        )
        depths_layout.addWidget(
            self._create_parameter_slider(DigitalPartialParameter.LFO_FILTER_DEPTH,
                                          "Filter")
        )
        depths_layout.addWidget(
            self._create_parameter_slider(DigitalPartialParameter.LFO_AMP_DEPTH,
                                          "Amp")
        )
        depths_layout.addWidget(
            self._create_parameter_slider(DigitalPartialParameter.LFO_PAN_DEPTH,
                                          "Pan")
        )
        layout.addWidget(depths_group)
        layout.addStretch()
        return lfo_section

    def _create_mod_lfo_section(self):
        """Create modulation LFO section"""
        mod_lfo_group_box = QWidget()
        mod_lfo_layout = QVBoxLayout()
        mod_lfo_group_box.setLayout(mod_lfo_layout)

        # Shape and sync controls
        top_row = QHBoxLayout()

        # Shape switch
        self.mod_lfo_shape = self._create_parameter_combo_box(
            DigitalPartialParameter.MOD_LFO_SHAPE,
            "Shape",
            [shape.display_name for shape in DigitalLFOShape]
        )
        self.mod_lfo_shape.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalPartialParameter.MOD_LFO_SHAPE, v)
        )
        top_row.addWidget(self.mod_lfo_shape)

        # Sync switch
        self.mod_lfo_sync = self._create_parameter_combo_box(
            DigitalPartialParameter.MOD_LFO_TEMPO_SYNC_SWITCH,
            "Sync",
            [switch.display_name for switch in DigitalLFOTempoSyncNote]
        )
        top_row.addWidget(self.mod_lfo_sync)
        mod_lfo_layout.addLayout(top_row)

        # Rate and note controls
        rate_row = QHBoxLayout()
        rate_row.addWidget(
            self._create_parameter_slider(DigitalPartialParameter.MOD_LFO_RATE, 
                                          "Rate")
        )
        # Note selection (only visible when sync is ON)
        self.mod_lfo_note = self._create_parameter_combo_box(
            DigitalPartialParameter.MOD_LFO_TEMPO_SYNC_NOTE,
            "Note",
            [note.display_name for note in DigitalLFOTempoSyncNote],
            [note.value for note in LFOSyncNote]
        )
        rate_row.addWidget(self.mod_lfo_note)
        mod_lfo_layout.addLayout(rate_row)

        # Modulation depths
        depths_group = QGroupBox("Depths")
        depths_layout = QVBoxLayout()
        depths_group.setLayout(depths_layout)

        depths_layout.addWidget(
            self._create_parameter_slider(DigitalPartialParameter.MOD_LFO_PITCH_DEPTH, 
                                          "Pitch")
        )
        depths_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParameter.MOD_LFO_FILTER_DEPTH, 
                "Filter"
            )
        )
        depths_layout.addWidget(
            self._create_parameter_slider(DigitalPartialParameter.MOD_LFO_AMP_DEPTH, 
                                          "Amp")
        )
        depths_layout.addWidget(
            self._create_parameter_slider(DigitalPartialParameter.MOD_LFO_PAN, 
                                          "Pan")
        )
        mod_lfo_layout.addWidget(depths_group)

        # Rate control
        mod_lfo_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParameter.MOD_LFO_RATE_CTRL, 
                "Rate Ctrl"
            )
        )
        mod_lfo_layout.addStretch()
        return mod_lfo_group_box

    def _on_waveform_selected(self, waveform: DigitalOscWave):
        """Handle waveform button clicks"""
        # Reset all buttons to default style
        for btn in self.wave_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(Style.JDXI_BUTTON_RECT)

        # Apply active style to the selected waveform button
        selected_btn = self.wave_buttons.get(waveform)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(Style.JDXI_BUTTON_RECT_ACTIVE)

        # Send MIDI message
        if not self.send_midi_parameter(DigitalPartialParameter.OSC_WAVE, waveform.value):
            logging.warning(f"Failed to set waveform to {waveform.name}")

        # Update control visibility
        self._update_pw_controls_state(waveform)
        self._update_pcm_controls_state(waveform)
