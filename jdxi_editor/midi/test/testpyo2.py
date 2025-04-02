from pyo import *
import time

# Initialize server
s = Server().boot()

# Create a sine wave oscillator
osc = Sine(freq=440, mul=0.5)

# Create a low-pass filter with an initial cutoff frequency
filter = ButLP(osc, freq=200, mul=0.5)

# Apply the filter to the output
filter.out()

# Start the server
s.start()

# Sweep the cutoff frequency from 200Hz to 2000Hz over 10 seconds
sweep_time = 10  # Total sweep time in seconds
start_freq = 200
end_freq = 2000
num_steps = 100  # Number of steps in the sweep

for i in range(num_steps):
    # Calculate the current frequency for this step
    current_freq = start_freq + (end_freq - start_freq) * (i / (num_steps - 1))

    # Set the filter frequency
    filter.setFreq(current_freq)

    # Wait for the next step
    time.sleep(sweep_time / num_steps)

# Stop the server after the sweep
s.stop()
