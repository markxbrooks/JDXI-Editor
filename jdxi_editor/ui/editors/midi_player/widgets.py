"""
UI components for MIDI file player.
"""

from PySide6.QtWidgets import QCheckBox, QLabel, QPushButton, QSlider

from jdxi_editor.ui.widgets.digital.title import DigitalTitle

from jdxi_editor.ui.widgets.midi.track_viewer import MidiTrackViewer


class MidiPlayerWidgets:
    """UI class for MIDI file player interface."""

    def __init__(self):
        """constructor"""
        self.pause_label = None
        self.automation_channel_combo = None
        self.automation_type_combo = None
        self.automation_program_combo = None
        self.file_auto_generate_checkbox = None
        self.digital_title_file_name = DigitalTitle("No file loaded")
        self.load_button = QPushButton()
        self.save_button = QPushButton()
        self.play_button = QPushButton()
        self.stop_button = QPushButton()
        self.pause_button = QPushButton()
        self.midi_file_position_slider = QSlider()
        self.midi_suppress_program_changes_checkbox = QCheckBox()
        self.midi_suppress_control_changes_checkbox = QCheckBox()
        self.position_label = QLabel()
        self.midi_track_viewer = MidiTrackViewer()
