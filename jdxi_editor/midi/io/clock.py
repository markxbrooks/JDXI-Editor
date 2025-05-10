import mido
import time

try:
    outport = mido.open_output()
except Exception as e:
    print(f"Error opening MIDI output port: {e}")
    exit()

clock_message = mido.Message('clock')
tempo = 120
time_per_pulse = (60 / tempo) / 24

try:
    while True:
        outport.send(clock_message)
        time.sleep(time_per_pulse)
except KeyboardInterrupt:
    print("Stopping MIDI clock.")
finally:
    outport.close()
