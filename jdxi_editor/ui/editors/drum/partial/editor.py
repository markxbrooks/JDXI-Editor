"""
This module defines the `DrumPartialEditor` class for editing drum kit parameters within a graphical user interface (GUI).

The `DrumPartialEditor` class allows users to modify various parameters related to drum sounds, including pitch, output, TVF (Time Variant Filter), pitch envelope, WMT (Wave Modulation Time), and TVA (Time Variant Amplitude) settings. The class provides a comprehensive layout with controls such as sliders, combo boxes, and spin boxes to adjust the parameters.

Key functionalities of the module include:
- Displaying parameter controls for a specific drum partial.
- Providing detailed access to different parameter groups such as pitch, output, and TVA.
- Handling MIDI and tone area settings for drum kit editing.
- Handling dynamic address assignment for each partial based on its name.

Dependencies:
- `logging`: For logging initialization and error handling.
- `PySide6.QtWidgets`: For GUI components such as `QWidget`, `QVBoxLayout`, `QScrollArea`, etc.
- `jdxi_manager.midi.data.drums`: For drum-related data and operations like retrieving drum waves.
- `jdxi_manager.midi.data.parameter.drums`: For specific drum parameter definitions and utilities.
- `jdxi_manager.midi.data.constants.sysex`: For MIDI-related constants like `TEMPORARY_TONE_AREA` and `DRUM_KIT_AREA`.
- `jdxi_manager.ui.widgets`: For custom UI widgets such as `Slider`, `ComboBox`, and `SpinBox`.

The `DrumPartialEditor` is designed to work within a larger system for managing drum kit tones, providing an intuitive interface for modifying various sound parameters.

"""
from typing import Dict, Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QGridLayout,
    QTabWidget,
)

from jdxi_editor.jdxi.synth.type import JDXiSynth
from jdxi_editor.midi.data.address.address import AddressOffsetProgramLMB
from jdxi_editor.midi.data.parameter.drum.addresses import DRUM_GROUP_MAP
from jdxi_editor.midi.data.parameter.drum.partial import AddressParameterDrumPartial
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.drum.partial.output import DrumOutputSection
from jdxi_editor.ui.editors.drum.partial.pitch import DrumPitchSection
from jdxi_editor.ui.editors.drum.partial.pitch_env import DrumPitchEnvSection
from jdxi_editor.ui.editors.drum.partial.tva import DrumTVASection
from jdxi_editor.ui.editors.drum.partial.tvf import DrumTVFSection
from jdxi_editor.ui.editors.drum.partial.wmt import DrumWMTSection
from jdxi_editor.ui.editors.synth.partial import PartialEditor


class DrumPartialEditor(PartialEditor):
    """Editor for address single partial"""

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        partial_number: int = 0,
        partial_name: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.partial_number = partial_number  # This is now the numerical index
        self.partial_name = partial_name  # This is now the numerical index
        self.partial_address_default = AddressOffsetProgramLMB.DRUM_DEFAULT_PARTIAL
        self.partial_address_map = DRUM_GROUP_MAP
        self.preset_helper = None
        self._init_synth_data(synth_type=JDXiSynth.DRUM_KIT, partial_number=self.partial_number)
        # Store parameter controls for easy access
        self.controls: Dict[AddressParameterDrumPartial, QWidget] = {}

        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)

        # Create grid layout for parameter groups
        grid_layout = QGridLayout()
        scroll_layout.addLayout(grid_layout)

        tab_widget = QTabWidget()
        scroll_layout.addWidget(tab_widget)

        tab_wmt = QWidget()
        tab_wmt_layout = QVBoxLayout(tab_wmt)
        tab_widget.addTab(tab_wmt, "WMT")

        wmt_group = DrumWMTSection(
            self.controls,
            self._create_parameter_combo_box,
            self._create_parameter_slider,
            self.midi_helper,
            address=self.address
        )
        tab_wmt_layout.addWidget(wmt_group)

        tab_pitch = QWidget()
        tab_pitch_layout = QVBoxLayout(tab_pitch)
        tab_widget.addTab(tab_pitch, "Pitch")

        pitch_group = DrumPitchSection(
            self.controls,
            self._create_parameter_combo_box,
            self._create_parameter_slider,
            self.midi_helper,
        )
        tab_pitch_layout.addWidget(pitch_group)

        tab_pitch_env = QWidget()
        tab_pitch_env_layout = QVBoxLayout(tab_pitch_env)
        tab_widget.addTab(tab_pitch_env, "Pitch Env")

        pitch_env_group = DrumPitchEnvSection(
            self.controls,
            self._create_parameter_combo_box,
            self._create_parameter_slider,
            self.midi_helper,
        )
        tab_pitch_env_layout.addWidget(pitch_env_group)

        tab_output = QWidget()
        tab_output_layout = QVBoxLayout(tab_output)
        tab_widget.addTab(tab_output, "Output")

        output_group = DrumOutputSection(
            self.controls,
            self._create_parameter_combo_box,
            self._create_parameter_slider,
            self.midi_helper,
        )
        tab_output_layout.addWidget(output_group)

        tab_tvf = QWidget()
        tab_tvf_layout = QVBoxLayout(tab_tvf)
        tab_widget.addTab(tab_tvf, "TVF")

        tvf_group = DrumTVFSection(
            self.controls,
            self._create_parameter_combo_box,
            self._create_parameter_slider,
            self.midi_helper,
        )
        tab_tvf_layout.addWidget(tvf_group)

        tab_tva = QWidget()
        tab_tva_layout = QVBoxLayout(tab_tva)
        tab_widget.addTab(tab_tva, "TVA")

        tva_group = DrumTVASection(
            self.controls,
            self._create_parameter_combo_box,
            self._create_parameter_slider,
            self.midi_helper,
        )
        tab_tva_layout.addWidget(tva_group)

        main_layout.addWidget(scroll_area)

