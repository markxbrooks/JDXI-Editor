"""UI components for MIDI file player."""

from PySide6.QtWidgets import QCheckBox, QComboBox, QLabel, QPushButton, QSlider

from jdxi_editor.ui.widgets.display.digital import DigitalTitle
from jdxi_editor.ui.widgets.midi.track_viewer import MidiTrackViewer


class UiMidi:
    """UI class for MIDI file player interface."""

    def __init__(self):
        self.automation_program_combo = None
        self.usb_file_auto_generate_checkbox = None
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
        self.usb_file_select = QPushButton()
        self.usb_file_output_name = ""
        self.usb_file_record_checkbox = QCheckBox()
        self.usb_port_select_combo = QComboBox()
        self.usb_port_refresh_devices_button = QPushButton()
