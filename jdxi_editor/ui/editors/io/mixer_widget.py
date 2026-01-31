"""
Program Mixer Widget Module

This module defines the `ProgramMixerWidget` class, a widget for managing
mixer level controls for all synthesizer parts (Master, Digital 1/2, Drums, Analog).

Classes:
    ProgramMixerWidget(SynthBase)
        A widget for displaying and controlling mixer levels.
"""

from typing import Dict, Optional

from decologr import Decologr as log
from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtWidgets import QGridLayout, QGroupBox, QLabel, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.core.synth.factory import create_synth_data
from jdxi_editor.core.synth.type import JDXiSynth
from jdxi_editor.midi.data.address.program import ProgramCommonAddress
from jdxi_editor.midi.data.parameter.analog.address import AnalogParam
from jdxi_editor.midi.data.parameter.digital import DigitalCommonParam
from jdxi_editor.midi.data.parameter.drum.common import DrumCommonParam
from jdxi_editor.midi.data.parameter.program.common import ProgramCommonParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.synth.base import SynthBase
from jdxi_editor.ui.widgets.editor.helper import create_group_with_layout


class ProgramMixerWidget(SynthBase):
    """Widget for managing mixer level controls."""

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize the ProgramMixerWidget.

        :param midi_helper: Optional[MidiIOHelper] for MIDI communication
        :param parent: Optional[QWidget] parent widget
        """
        super().__init__(midi_helper=midi_helper, parent=parent)
        self.mixer_group: Optional[QGroupBox] = None
        self.mixer_layout: Optional[QGridLayout] = None

        # Labels for displaying current program/synth names
        self.master_level_current_label: Optional[QLabel] = None
        self.digital_synth_1_current_label: Optional[QLabel] = None
        self.digital_synth_2_current_label: Optional[QLabel] = None
        self.drum_kit_current_label: Optional[QLabel] = None
        self.analog_synth_current_label: Optional[QLabel] = None

        # Sliders
        self.master_level_slider = None
        self.digital1_level_slider = None
        self.digital2_level_slider = None
        self.drums_level_slider = None
        self.analog_level_slider = None

        # Icons and titles
        self.master_level_icon: Optional[QLabel] = None
        self.digital_synth_1_icon: Optional[QLabel] = None
        self.digital_synth_2_icon: Optional[QLabel] = None
        self.drum_kit_icon: Optional[QLabel] = None
        self.analog_synth_icon: Optional[QLabel] = None

    def create_mixer_widget(self) -> QGroupBox:
        """
        Create and return the mixer group widget with all controls.

        :return: QGroupBox containing the mixer controls
        """
        # Create mixer layout and group
        self.mixer_layout = QGridLayout()
        self.mixer_group, _ = create_group_with_layout(
            label="Mixer Level Settings", child_layout=self.mixer_layout
        )

        # Create labels and icons
        self._create_labels_and_icons()

        # Create sliders
        self._create_sliders()

        # Populate layout
        self._populate_layout()

        # Apply styling
        JDXi.UI.Theme.apply_adsr_style(widget=self.mixer_group)
        if self.analog_level_slider:
            JDXi.UI.Theme.apply_adsr_style(widget=self.analog_level_slider)

        return self.mixer_group

    def _create_labels_and_icons(self) -> None:
        """Create all labels and icons for the mixer."""
        # Master Level
        self.master_level_icon = QLabel()
        self.master_level_icon.setPixmap(
            JDXi.UI.Icon.get_icon(JDXi.UI.Icon.KEYBOARD).pixmap(40, 40)
        )
        self.master_level_current_label = QLabel("Current Program")
        JDXi.UI.Theme.apply_mixer_label(self.master_level_current_label)

        # Digital Synth 1
        self.digital_synth_1_icon = QLabel()
        self.digital_synth_1_icon.setPixmap(
            JDXi.UI.Icon.get_icon_pixmap(
                JDXi.UI.Icon.PIANO, color=JDXi.UI.Style.FOREGROUND, size=40
            )
        )
        self.digital_synth_1_current_label = QLabel("Current Synth:")
        JDXi.UI.Theme.apply_mixer_label(self.digital_synth_1_current_label)

        # Digital Synth 2
        self.digital_synth_2_icon = QLabel()
        self.digital_synth_2_icon.setPixmap(
            JDXi.UI.Icon.get_icon_pixmap(
                JDXi.UI.Icon.PIANO, color=JDXi.UI.Style.FOREGROUND, size=40
            )
        )
        self.digital_synth_2_current_label = QLabel("Current Synth:")
        JDXi.UI.Theme.apply_mixer_label(self.digital_synth_2_current_label)

        # Drum Kit
        self.drum_kit_icon = QLabel()
        self.drum_kit_icon.setPixmap(
            JDXi.UI.Icon.get_icon_pixmap(
                JDXi.UI.Icon.DRUM, color=JDXi.UI.Style.FOREGROUND, size=40
            )
        )
        self.drum_kit_current_label = QLabel("Current Synth:")
        JDXi.UI.Theme.apply_mixer_label(self.drum_kit_current_label)

        # Analog Synth
        self.analog_synth_icon = QLabel()
        self.analog_synth_icon.setPixmap(
            JDXi.UI.Icon.get_icon_pixmap(
                JDXi.UI.Icon.PIANO, color=JDXi.UI.Style.FOREGROUND, size=40
            )
        )
        self.analog_synth_current_label = QLabel("Current Synth:")
        JDXi.UI.Theme.apply_mixer_label(self.analog_synth_current_label, analog=True)

    def _create_sliders(self) -> None:
        """Create all mixer sliders."""
        # Master Level (Program Common)
        program_common_address = ProgramCommonAddress()
        self.address = program_common_address
        self.master_level_slider = self._create_parameter_slider(
            param=ProgramCommonParam.PROGRAM_LEVEL,
            label="Master",
            vertical=True,
            address=program_common_address,
        )
        self.controls[ProgramCommonParam.PROGRAM_LEVEL] = self.master_level_slider

        # Digital Synth 1
        self._init_synth_data(synth_type=JDXiSynth.DIGITAL_SYNTH_1)
        self.digital1_level_slider = self._create_parameter_slider(
            DigitalCommonParam.TONE_LEVEL, "Digital 1", vertical=True
        )
        self.controls[DigitalCommonParam.TONE_LEVEL] = self.digital1_level_slider

        # Digital Synth 2
        self._init_synth_data(synth_type=JDXiSynth.DIGITAL_SYNTH_2)
        self.digital2_level_slider = self._create_parameter_slider(
            DigitalCommonParam.TONE_LEVEL, "Digital 2", vertical=True
        )
        # Note: We're reusing TONE_LEVEL param, but the address is different
        # The slider will use the current self.address which was set by _init_synth_data
        # We don't store digital2 in controls dict since it would overwrite digital1
        # Both sliders are accessed directly via widget references

        # Drum Kit
        self._init_synth_data(synth_type=JDXiSynth.DRUM_KIT)
        self.drums_level_slider = self._create_parameter_slider(
            DrumCommonParam.KIT_LEVEL, "Drums", vertical=True
        )
        self.controls[DrumCommonParam.KIT_LEVEL] = self.drums_level_slider

        # Analog Synth
        self._init_synth_data(synth_type=JDXiSynth.ANALOG_SYNTH)
        self.analog_level_slider = self._create_parameter_slider(
            AnalogParam.AMP_LEVEL, "Analog", vertical=True
        )
        self.controls[AnalogParam.AMP_LEVEL] = self.analog_level_slider

        # Reset address to program common
        self.address = program_common_address

    def _init_synth_data(
        self,
        synth_type: str = JDXiSynth.DIGITAL_SYNTH_1,
        partial_number: Optional[int] = 0,
    ) -> None:
        """
        Initialize synth-specific data for slider creation.

        :param synth_type: JDXiSynth synth type
        :param partial_number: int partial number (default 0)
        """
        synth_data = create_synth_data(synth_type, partial_number=partial_number)
        self.address = synth_data.address

    def _populate_layout(self) -> None:
        """Populate the mixer layout with widgets."""
        if not self.mixer_layout:
            return

        # Set column stretches
        self.mixer_layout.setColumnStretch(0, 1)
        self.mixer_layout.setColumnStretch(6, 1)

        # Row 0: Sliders
        if self.master_level_slider:
            self.mixer_layout.addWidget(self.master_level_slider, 0, 1)
        if self.digital1_level_slider:
            self.mixer_layout.addWidget(self.digital1_level_slider, 0, 2)
        if self.digital2_level_slider:
            self.mixer_layout.addWidget(self.digital2_level_slider, 0, 3)
        if self.drums_level_slider:
            self.mixer_layout.addWidget(self.drums_level_slider, 0, 4)
        if self.analog_level_slider:
            self.mixer_layout.addWidget(self.analog_level_slider, 0, 5)

        # Row 1: Current labels
        if self.master_level_current_label:
            self.mixer_layout.addWidget(self.master_level_current_label, 1, 1)
        if self.digital_synth_1_current_label:
            self.mixer_layout.addWidget(self.digital_synth_1_current_label, 1, 2)
        if self.digital_synth_2_current_label:
            self.mixer_layout.addWidget(self.digital_synth_2_current_label, 1, 3)
        if self.drum_kit_current_label:
            self.mixer_layout.addWidget(self.drum_kit_current_label, 1, 4)
        if self.analog_synth_current_label:
            self.mixer_layout.addWidget(self.analog_synth_current_label, 1, 5)

        # Row 2: Icons
        if self.master_level_icon:
            self.mixer_layout.addWidget(self.master_level_icon, 2, 1)
        if self.digital_synth_1_icon:
            self.mixer_layout.addWidget(self.digital_synth_1_icon, 2, 2)
        if self.digital_synth_2_icon:
            self.mixer_layout.addWidget(self.digital_synth_2_icon, 2, 3)
        if self.drum_kit_icon:
            self.mixer_layout.addWidget(self.drum_kit_icon, 2, 4)
        if self.analog_synth_icon:
            self.mixer_layout.addWidget(self.analog_synth_icon, 2, 5)

    def update_tone_name_for_synth(self, tone_name: str, synth_type: str) -> None:
        """
        Update the tone name for a specific synth.

        :param tone_name: str tone name to display
        :param synth_type: str synth type (JDXiSynth constant)
        """
        log.message(f"Update tone name triggered: tone_name {tone_name} {synth_type}")
        synth_label_map = {
            JDXiSynth.DIGITAL_SYNTH_1: self.digital_synth_1_current_label,
            JDXiSynth.DIGITAL_SYNTH_2: self.digital_synth_2_current_label,
            JDXiSynth.DRUM_KIT: self.drum_kit_current_label,
            JDXiSynth.ANALOG_SYNTH: self.analog_synth_current_label,
        }

        label = synth_label_map.get(synth_type)
        if label:
            try:
                label.setText(tone_name)
            except Exception as ex:
                log.message(f"Error {ex} setting text")
        else:
            log.warning(
                f"synth type: {synth_type} not found in mapping. Cannot update tone name."
            )

    def update_program_name(self, program_name: str) -> None:
        """
        Update the master level label with the current program name.

        :param program_name: str program name to display
        """
        if self.master_level_current_label:
            self.master_level_current_label.setText(program_name or "Current Program")

    def get_controls(self) -> Dict[AddressParameter, QWidget]:
        """
        Get the controls dictionary for access by parent.

        :return: Dict[AddressParameter, QWidget] controls dictionary
        """
        return self.controls
