"""
UI components for MIDI file player.
"""

from PySide6.QtWidgets import QCheckBox, QLabel, QSlider

from jdxi_editor.ui.widgets.digital.title import DigitalTitle

from jdxi_editor.ui.widgets.midi.track_viewer import MidiTrackViewer


class MidiPlayerWidgets:
    """UI class for MIDI file player interface."""

    def __init__(self):
        """constructor"""
        self.digital_title_file_name = DigitalTitle("No file loaded")
        self.midi_suppress_program_changes_checkbox = QCheckBox()
        self.midi_suppress_control_changes_checkbox = QCheckBox()
