"""

# Set up MIDI output
midiout = rtmidi.MidiOut()
midiout.open_port(0)  # or use open_virtual_port("name")

# Change LFO Pitch Depth for Partial 2 (NRPN MSB 0, LSB 16), value = 100
send_nrpn(midiout, channel=0, nrpn_msb=0, nrpn_lsb=16, value=100)

midiout.close_port()

"""

import rtmidi


class MidiTestController:
    def __init__(self, port_name=None):
        self.midiout = rtmidi.MidiOut()
        ports = self.midiout.get_ports()

        if port_name:
            if port_name in ports:
                self.midiout.open_port(ports.index(port_name))
            else:
                raise ValueError(f"MIDI port '{port_name}' not found.")
        else:
            if ports:
                self.midiout.open_port(0)
            else:
                self.midiout.open_virtual_port("Virtual MIDI Controller")

    def close(self):
        self.midiout.close_port()

    def send_cc(self, channel, control, value):
        status = 0xB0 | (channel & 0x0F)
        self.midiout.send_message([status, control, value])

    def send_value(self, channel, msb, lsb=None):
        self.send_cc(channel, 6, msb)  # Data Entry MSB
        if lsb is not None:
            self.send_cc(channel, 38, lsb)  # Data Entry LSB

    def send_nrpn(self, channel, nrpn_msb, nrpn_lsb, value, reset=True):
        self.send_cc(channel, 99, nrpn_msb)  # NRPN MSB
        self.send_cc(channel, 98, nrpn_lsb)  # NRPN LSB
        self.send_value(channel, value)

        if reset:
            self.send_cc(channel, 99, 127)  # Reset NRPN MSB
            self.send_cc(channel, 98, 127)  # Reset NRPN LSB

    def send_rpn(self, channel, rpn_msb, rpn_lsb, value, reset=True):
        self.send_cc(channel, 101, rpn_msb)  # RPN MSB
        self.send_cc(channel, 100, rpn_lsb)  # RPN LSB
        self.send_value(channel, value)

        if reset:
            self.send_cc(channel, 101, 127)  # Reset RPN MSB
            self.send_cc(channel, 100, 127)  # Reset RPN LSB
