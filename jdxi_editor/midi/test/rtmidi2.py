import mido
import time

def callback(message, time_stamp):
    print(message, time_stamp)

class MidiHelper:
    def __init__(self):
        self.midiin = mido.open_input('JD-Xi')

    def set_callback(self, callback):
        self.midiin.set_callback(callback)

    def get_ports(self):
        return self.midiin.get_ports()

midi_helper = MidiHelper()
midi_helper.set_callback(callback)

# Keep the script running to receive MIDI messages
while True:
    time.sleep(0.1)