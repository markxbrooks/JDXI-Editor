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
from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
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
from jdxi_editor.ui.editors.address.factory import create_arp_address
from jdxi_editor.ui.editors.synth.simple import BasicEditor
from jdxi_editor.ui.preset.helper import JDXiPresetHelper
from jdxi_editor.ui.widgets.editor.base import EditorBaseWidget
from jdxi_editor.ui.widgets.editor.helper import transfer_layout_items
from jdxi_editor.ui.widgets.editor.simple_editor_helper import SimpleEditorHelper


class ArpeggioEditor(BasicEditor):
    """Arpeggio Editor Window"""

    def __init__(
        self,
        midi_helper: MidiIOHelper,
        preset_helper: Optional[JDXiPresetHelper] = None,
        parent: Optional["JDXiInstrument"] = None,
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
        self.address = create_arp_address()
        self.partial_number = 0
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

        # --- Use EditorBaseWidget for consistent scrollable layout structure
        self.base_widget = EditorBaseWidget(parent=self, analog=False)
        self.base_widget.setup_scrollable_content()

        # --- Use SimpleEditorHelper for standardized title/image/tab setup
        self.editor_helper = SimpleEditorHelper(
            editor=self,
            base_widget=self.base_widget,
            title="Arpeggiator",
            image_folder="arpeggiator",
            default_image="arpeggiator2.png",
        )

        # --- Get rows layout to add additional content (icon row and switches)
        # Helper function to create left-aligned horizontal layouts
        def create_left_aligned_row(widget_list: list) -> QHBoxLayout:
            """Create a left-aligned horizontal layout"""
            row = QHBoxLayout()
            for widget in widget_list:
                row.addWidget(widget)
            row.addStretch()  # Only add stretch on the right
            return row

        # --- Icons row (standardized across editor tabs) - transfer items to avoid "already has a parent" errors
        icon_row_container = QHBoxLayout()
        icon_hlayout = JDXi.UI.Icon.create_generic_musical_icon_row()

        transfer_layout_items(icon_hlayout, icon_row_container)
        # Add on-off switch
        common_button = self._create_parameter_switch(
            ProgramZoneParam.ARPEGGIO_SWITCH,
            "Master Arpeggiator",
            [switch_setting.display_name for switch_setting in ArpeggioSwitch],
        )
        program_zone_row = create_left_aligned_row([common_button])
        # Add on-off switch
        self.switch_button = self._create_parameter_switch(
            ArpeggioParam.ARPEGGIO_SWITCH,
            "Arpeggiator",
            [switch_setting.display_name for switch_setting in ArpeggioSwitch],
        )
        switch_row = create_left_aligned_row([self.switch_button])
        # --- Create address combo box for Arpeggio Style
        self.style_combo = self._create_parameter_combo_box(
            ArpeggioParam.ARPEGGIO_STYLE, "Style", ARPEGGIO_STYLE
        )
        style_row = create_left_aligned_row([self.style_combo])
        # Create address combo box for Arpeggio Grid
        # Add grid combo box
        self.grid_combo = self._create_parameter_combo_box(
            ArpeggioParam.ARPEGGIO_GRID,
            "Grid:",
            [grid.display_name for grid in ArpeggioGrid],
        )
        grid_row = create_left_aligned_row([self.grid_combo])
        # Add grid combo box
        # Create address combo box for Arpeggio Duration
        self.duration_combo = self._create_parameter_combo_box(
            ArpeggioParam.ARPEGGIO_DURATION,
            "Duration",
            [duration.display_name for duration in ArpeggioDuration],
        )
        duration_row = create_left_aligned_row([self.duration_combo])
        # --- Add sliders
        self.velocity_slider = self._create_parameter_slider(
            ArpeggioParam.ARPEGGIO_VELOCITY, "Velocity", 0, 127
        )
        self.accent_slider = self._create_parameter_slider(
            ArpeggioParam.ARPEGGIO_ACCENT_RATE, "Accent", 0, 127
        )
        # --- Add octave range combo box
        self.octave_combo = self._create_parameter_combo_box(
            ArpeggioParam.ARPEGGIO_OCTAVE_RANGE,
            "Octave Range:",
            [octave.display_name for octave in ArpeggioOctaveRange],
            [octave.midi_value for octave in ArpeggioOctaveRange],
        )
        # --- Set default to 0
        self.octave_combo.combo_box.setCurrentIndex(3)  # Index 3 is OCT_ZERO
        octave_row = create_left_aligned_row([self.octave_combo])
        # --- Add motif combo box
        self.motif_combo = self._create_parameter_combo_box(
            ArpeggioParam.ARPEGGIO_MOTIF,
            "Motif:",
            [motif.name for motif in ArpeggioMotif],
        )
        motif_row = create_left_aligned_row([self.motif_combo])

        self.create_rows_layout(
            {
                "duration_row": duration_row,
                "grid_row": grid_row,
                "icon_hlayout": icon_hlayout,
                "motif_row": motif_row,
                "octave_row": octave_row,
                "program_zone_row": program_zone_row,
                "style_row": style_row,
                "switch_row": switch_row,
                "velocity_slider": self.velocity_slider,
                "accent_slider": self.accent_slider,
            }
        )

        # Add base widget to editor's layout
        if not hasattr(self, "main_layout") or self.main_layout is None:
            self.main_layout = QVBoxLayout(self)
            self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.base_widget)

    def create_rows_layout(self, widgets_dict: dict):
        """create rows layout"""
        rows_layout = self.editor_helper.get_rows_layout()
        # Add all layouts and widgets
        rows_layout.addLayout(widgets_dict["icon_hlayout"])
        rows_layout.addLayout(widgets_dict["program_zone_row"])
        rows_layout.addLayout(widgets_dict["switch_row"])
        rows_layout.addLayout(widgets_dict["style_row"])
        rows_layout.addLayout(widgets_dict["grid_row"])
        rows_layout.addLayout(widgets_dict["duration_row"])
        rows_layout.addWidget(widgets_dict["velocity_slider"])
        rows_layout.addWidget(widgets_dict["accent_slider"])
        rows_layout.addLayout(widgets_dict["octave_row"])
        rows_layout.addLayout(widgets_dict["motif_row"])
        rows_layout.addStretch()
