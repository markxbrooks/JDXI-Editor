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
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QGridLayout, QGroupBox, QLabel, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.core.synth.factory import create_synth_data
from jdxi_editor.core.synth.type import JDXiSynth
from jdxi_editor.midi.data.address.address import JDXiSysExAddress
from jdxi_editor.midi.data.address.program import ProgramCommonAddress
from jdxi_editor.midi.data.parameter.analog.address import AnalogParam
from jdxi_editor.midi.data.parameter.digital import DigitalCommonParam
from jdxi_editor.midi.data.parameter.drum.common import DrumCommonParam
from jdxi_editor.midi.data.parameter.program.common import ProgramCommonParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.program.mixer.widgets import LabelWidgetRegistry
from jdxi_editor.ui.editors.program.track import MixerTrack, MixerTrackEntity
from jdxi_editor.ui.editors.synth.base import SynthBase
from jdxi_editor.ui.widgets.editor.helper import create_group_with_layout


class ProgramMixer(SynthBase):
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
        self.label_widgets = LabelWidgetRegistry()

        # Sliders
        self.master_level_slider: QWidget | None = None
        self.digital1_level_slider: QWidget | None = None
        self.digital2_level_slider: QWidget | None = None
        self.drums_level_slider: QWidget | None = None
        self.analog_level_slider: QWidget | None = None

        # Track addresses (for mute functionality)
        self.master_level_address: Optional[ProgramCommonAddress] = None
        self.digital1_level_address: Optional[JDXiSysExAddress] = None
        self.digital2_level_address: Optional[JDXiSysExAddress] = None
        self.drums_level_address: Optional[JDXiSysExAddress] = None
        self.analog_level_address: Optional[JDXiSysExAddress] = None

    def _make_track(
        self,
        entity: MixerTrackEntity,
        param: AddressParameter,
        synth_type: str | None,
        label_text: str,
        icon: QIcon,
        address: JDXiSysExAddress | ProgramCommonAddress,
    ) -> MixerTrack:

        slider = self._create_parameter_slider(
            param=param,
            label=label_text,
            vertical=True,
            address=address,
        )
        if synth_type == JDXiSynth.ANALOG_SYNTH:
            analog = True
        else:
            analog = False
        # Track name (static)
        name_label = QLabel(label_text)
        JDXi.UI.Theme.apply_mixer_label(name_label, analog=analog)

        # Value label (dynamic)
        value_label = QLabel("---")
        JDXi.UI.Theme.apply_mixer_label(value_label, analog=analog)
        if synth_type:
            self.label_widgets.register(synth_type, value_label)

        # Icon
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignHCenter)
        icon_label.setPixmap(icon.pixmap(32, 32))

        return MixerTrack(
            entity=entity,
            slider=slider,
            value_label=value_label,
            icon=icon_label,
            label=name_label,
            param=param,
            address=address,
            send_midi_callback=self.send_midi_parameter,
            analog=analog,
        )

    def _build_tracks(self):
        """build tracks"""
        pc_addr = ProgramCommonAddress()

        self.tracks = [
            self._make_track(
                MixerTrackEntity.MASTER,
                ProgramCommonParam.PROGRAM_LEVEL,
                JDXiSynth.MASTER,
                "Master",
                JDXi.UI.Icon.get_icon(JDXi.UI.Icon.KEYBOARD),
                pc_addr,
            ),
            self._track_for_synth(
                JDXiSynth.DIGITAL_SYNTH_1, "Digital 1", DigitalCommonParam.TONE_LEVEL
            ),
            self._track_for_synth(
                JDXiSynth.DIGITAL_SYNTH_2, "Digital 2", DigitalCommonParam.TONE_LEVEL
            ),
            self._track_for_synth(
                JDXiSynth.DRUM_KIT, "Drums", DrumCommonParam.KIT_LEVEL
            ),
            self._track_for_synth(
                JDXiSynth.ANALOG_SYNTH, "Analog", AnalogParam.AMP_LEVEL
            ),
        ]
        # Assign level sliders so the program editor can pass them to _update_slider for
        # incoming MIDI (self.controls has only one TONE_LEVEL key, so Digital 1 would
        # otherwise get Digital 2’s slider when using controls.get(param))
        self.master_level_slider = self.tracks[0].slider
        self.digital1_level_slider = self.tracks[1].slider
        self.digital2_level_slider = self.tracks[2].slider
        self.drums_level_slider = self.tracks[3].slider
        self.analog_level_slider = self.tracks[4].slider

    def _track_for_synth(self, synth: str, name: str, param: AddressParameter):
        """track for synth"""
        synth_data = create_synth_data(synth)
        return self._make_track(
            MixerTrackEntity.from_synth(synth),
            param,
            synth,
            name,
            JDXi.UI.Icon.icon_for_synth(synth),
            synth_data.address,
        )

    def _populate_layout(self) -> None:
        if not self.mixer_layout:
            return

        self.mixer_layout.setColumnStretch(0, 1)
        self.mixer_layout.setColumnStretch(len(self.tracks) + 1, 1)

        for col, track in enumerate(self.tracks, start=1):
            strip = track.build_strip()
            self.mixer_layout.addWidget(
                strip,
                0,
                col,
                1,
                1,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
            )
            JDXi.UI.Theme.apply_adsr_style(track.slider, track.analog)

        self.mixer_layout.setRowStretch(0, 1)

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

        # Build Tracks
        self._build_tracks()

        # Populate layout
        self._populate_layout()

        # Apply styling
        JDXi.UI.Theme.apply_adsr_style(widget=self.mixer_group)
        if self.analog_level_slider:
            JDXi.UI.Theme.apply_adsr_style(widget=self.analog_level_slider, analog=True)

        return self.mixer_group

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

    def update_tone_name_for_synth(self, tone_name: str, synth_type: str) -> None:
        """Update tone name for synth"""
        log.message(f"Update tone name triggered: {tone_name} {synth_type}")

        label = self.label_widgets.get(synth_type)
        if label:
            label.setText(tone_name)
        else:
            log.warning(
                f"synth type: {synth_type} not registered in mixer",
                scope=self.__class__.__name__,
            )

    def update_program_name(self, program_name: str) -> None:
        """
        Update the master level label with the current program name.

        :param program_name: str program name to digital
        """
        master_level = self.label_widgets.get(JDXiSynth.MASTER)
        if master_level:
            master_level.setText(program_name or "Current Program")

    def get_controls(self) -> Dict[AddressParameter, QWidget]:
        """
        Get the controls dictionary for access by parent.

        :return: Dict[AddressParameter, QWidget] controls dictionary
        """
        return self.controls
