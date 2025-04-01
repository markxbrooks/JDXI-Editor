import sys
import rtmidi
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

class MidiHandler:
    def __init__(self, midiin):
        self.midiin = midiin
        self.midiin.set_callback(self.midi_callback)

    def midi_callback(self, message, data):
        print(f"Received MIDI message: {message}")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_midi()

    def init_ui(self):
        self.setWindowTitle("MIDI Callback Example")
        self.setGeometry(100, 100, 400, 200)
        self.label = QLabel("Waiting for MIDI messages...", self)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def init_midi(self):
        self.midiin = rtmidi.MidiIn()
        available_ports = self.midiin.get_ports()
        if available_ports:
            self.midiin.open_port(0)
        else:
            self.midiin.open_virtual_port("My virtual input")

        self.midi_handler = MidiHandler(self.midiin)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())