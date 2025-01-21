import mido
import time

# Create a MIDI output port
try:
    outport = mido.open_output()
except:
    print("No MIDI output port found.")
    exit()

# Define a sequence
sequence = [
    mido.Message('note_on', note=60, velocity=127),  # C4
    mido.Message('note_off', note=60, velocity=0),
    mido.Message('note_on', note=64, velocity=127),  # E4
    mido.Message('note_off', note=64, velocity=0),
    mido.Message('note_on', note=67, velocity=127),  # G4
    mido.Message('note_off', note=67, velocity=0)
]

# Play the sequence
while True:
    for msg in sequence:
        outport.send(msg)
        time.sleep(0.5)  # Adjust the tempo here
