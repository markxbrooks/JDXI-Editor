from pyo import *

# Initialize server
s = Server().boot()

# Create oscillators
osc = Sine(freq=440, mul=0.5).out()

# Start server (this is where you can control synthesis in real-time)
s.start()

# Change frequency using MIDI or programmatically
osc.setFreq(880)  # Change frequency to 880Hz (A4)

# Keep server running for some time
time.sleep(5)

# Stop server
s.stop()
