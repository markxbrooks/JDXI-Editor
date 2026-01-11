"""
Arpeggio Editor Module

This module defines the `ArpeggioEditor` class, a specialized editor for configuring arpeggiator
settings within a synthesizer. It extends the `SynthEditor` class, providing a user-friendly
interface to control various arpeggiator parameters.

Classes:
    - ArpeggioEditor: A `QWidget` subclass that allows users to modify arpeggiator parameters
      such as style, grid, duration, velocity, accent, swing, octave range, and motif.

Features:
    - Provides an intuitive UI with labeled controls and dropdown menus for parameter selection.
    - Includes a toggle switch to enable or disable the arpeggiator.
    - Displays an instrument image for better user engagement.
    - Uses MIDI integration to send real-time parameter changes to the synthesizer.
    - Supports dynamic visualization and interaction through sliders and combo boxes.

Usage:
    ```python
    from PySide6.QtWidgets import QApplication
    from midi_helper import MIDIHelper

    app = QApplication([])
    midi_helper = MIDIHelper()
    editor = ArpeggioEditor(midi_helper=midi_helper)
    editor.show()
    app.exec()
    ```

Dependencies:
    - PySide6 (for UI components)
    - MIDIHelper (for MIDI communication)
    - ArpeggioParameter (for managing parameter addresses and value ranges)
    - Slider (for smooth control over numerical parameters)

"""

from typing import Dict, Optional

from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.jdxi.preset.helper import JDXiPresetHelper
from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.midi.data.address.address import ZERO_BYTE, RolandSysExAddress
from jdxi_editor.midi.data.address.arpeggio import ArpeggioAddress
from jdxi_editor.midi.data.arpeggio.arpeggio import (
    ArpeggioDuration,
    ArpeggioGrid,
    ArpeggioMotif,
    ArpeggioOctaveRange,
    ArpeggioSwitch,
)
from jdxi_editor.midi.data.arpeggio.data import (
    ARPEGGIO_STYLE,
)
from jdxi_editor.midi.data.parameter.arpeggio import ArpeggioParam
from jdxi_editor.midi.data.parameter.program.zone import ProgramZoneParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.synth.simple import BasicEditor
from jdxi_editor.ui.widgets.display.digital import DigitalTitle


class ArpeggioEditor(BasicEditor):
    """Arpeggio Editor Window"""

    def __init__(
        self,
        midi_helper: MidiIOHelper,
        preset_helper: Optional[JDXiPresetHelper] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(midi_helper=midi_helper, parent=parent)
        """
        Initialize the ArpeggioEditor

        :param midi_helper: MidiIOHelper
        :param preset_helper: JDXIPresetHelper
        :param parent: QWidget
        """
        self.setWindowTitle("Arpeggio Editor")
        self.midi_helper = midi_helper
        self.preset_helper = preset_helper
        self.address = RolandSysExAddress(
            msb=ArpeggioAddress.TEMPORARY_PROGRAM,
            umb=ArpeggioAddress.ARP_PART,
            lmb=ArpeggioAddress.ARP_GROUP,
            lsb=ZERO_BYTE,
        )
        self.partial_number = 0
        self.instrument_icon_folder = "arpeggiator"
        self.default_image = "arpeggiator2.png"
        self.controls: Dict[AddressParameter, QWidget] = {}

        if parent:
            if parent.current_synth_type:
                if parent.current_synth_type == "Digital 1":
                    self.partial_number = 0
                elif parent.current_synth_type == "Digital 2":
                    self.partial_number = 1
                elif parent.current_synth_type == "Digital 3":
                    self.partial_number = 2
                elif parent.current_synth_type == "Digital 4":
                    self.partial_number = 3

        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.title_label = DigitalTitle(tone_name="Arpeggiator")
        from jdxi_editor.jdxi.style.theme_manager import JDXiThemeManager

        JDXiThemeManager.apply_instrument_title_label(self.title_label)

        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center align the image

        title_group_box = QGroupBox()
        title_group_layout = QHBoxLayout()
        title_group_box.setLayout(title_group_layout)
        title_group_layout.addWidget(self.title_label)
        title_group_layout.addWidget(self.image_label)

        self.update_instrument_image()

        main_row_hlayout = QHBoxLayout()
        layout.addLayout(main_row_hlayout)
        main_row_hlayout.addStretch()
        rows_layout = QVBoxLayout()
        main_row_hlayout.addLayout(rows_layout)
        rows_layout.addWidget(title_group_box)
        # Add on-off switch
        program_zone_row = QHBoxLayout()
        common_button = self._create_parameter_switch(
            ProgramZoneParam.ARPEGGIO_SWITCH,
            "Master Arpeggiator",
            [switch_setting.display_name for switch_setting in ArpeggioSwitch],
        )
        program_zone_row.addWidget(common_button)

        rows_layout.addLayout(program_zone_row)

        # Add on-off switch
        switch_row = QHBoxLayout()
        self.switch_button = self._create_parameter_switch(
            ArpeggioParam.ARPEGGIO_SWITCH,
            "Arpeggiator",
            [switch_setting.display_name for switch_setting in ArpeggioSwitch],
        )
        switch_row.addWidget(self.switch_button)
        rows_layout.addLayout(switch_row)

        # Create address combo box for Arpeggio Style
        self.style_combo = self._create_parameter_combo_box(
            ArpeggioParam.ARPEGGIO_STYLE, "Style", ARPEGGIO_STYLE
        )
        style_row = QHBoxLayout()
        style_row.addWidget(self.style_combo)
        rows_layout.addLayout(style_row)

        # Create address combo box for Arpeggio Grid
        # Add grid combo box
        grid_row = QHBoxLayout()
        self.grid_combo = self._create_parameter_combo_box(
            ArpeggioParam.ARPEGGIO_GRID,
            "Grid:",
            [grid.display_name for grid in ArpeggioGrid],
        )
        grid_row.addWidget(self.grid_combo)
        rows_layout.addLayout(grid_row)

        # Add grid combo box
        duration_row = QHBoxLayout()
        # Create address combo box for Arpeggio Duration
        self.duration_combo = self._create_parameter_combo_box(
            ArpeggioParam.ARPEGGIO_DURATION,
            "Duration",
            [duration.display_name for duration in ArpeggioDuration],
        )
        duration_row.addWidget(self.duration_combo)
        rows_layout.addLayout(duration_row)

        # Add sliders
        self.velocity_slider = self._create_parameter_slider(
            ArpeggioParam.ARPEGGIO_VELOCITY, "Velocity", 0, 127
        )
        rows_layout.addWidget(self.velocity_slider)

        self.accent_slider = self._create_parameter_slider(
            ArpeggioParam.ARPEGGIO_ACCENT_RATE, "Accent", 0, 127
        )
        rows_layout.addWidget(self.accent_slider)

        # Add octave range combo box
        octave_row = QHBoxLayout()
        self.octave_combo = self._create_parameter_combo_box(
            ArpeggioParam.ARPEGGIO_OCTAVE_RANGE,
            "Octave Range:",
            [octave.display_name for octave in ArpeggioOctaveRange],
            [octave.midi_value for octave in ArpeggioOctaveRange],
        )
        # Set default to 0
        self.octave_combo.combo_box.setCurrentIndex(3)  # Index 3 is OCT_ZERO
        octave_row.addWidget(self.octave_combo)
        rows_layout.addLayout(octave_row)

        # Add motif combo box
        motif_row = QHBoxLayout()
        self.motif_combo = self._create_parameter_combo_box(
            ArpeggioParam.ARPEGGIO_MOTIF,
            "Motif:",
            [motif.name for motif in ArpeggioMotif],
        )
        motif_row.addWidget(self.motif_combo)
        rows_layout.addLayout(motif_row)
        rows_layout.addStretch()
        main_row_hlayout.addStretch()
