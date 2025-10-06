"""
rtmidi Compatibility Module

This module provides compatibility between different versions of rtmidi.
It creates wrapper classes that match the older MidiIn/MidiOut API expected by the JD-Xi Editor codebase.
"""

import rtmidi


class MidiIn:
    """Compatibility wrapper for RtMidiIn"""
    
    def __init__(self):
        self._midi = rtmidi.RtMidiIn()
    
    def get_ports(self):
        """Get list of available input ports"""
        ports = []
        for i in range(self._midi.getPortCount()):
            ports.append(self._midi.getPortName(i))
        return ports
    
    def is_port_open(self):
        """Check if port is open"""
        return self._midi.isPortOpen()
    
    def open_port(self, port):
        """Open port by name or index"""
        if isinstance(port, str):
            # Find port by name
            for i in range(self._midi.getPortCount()):
                if self._midi.getPortName(i) == port:
                    return self._midi.openPort(i)
            raise ValueError(f"Port '{port}' not found")
        else:
            # Assume it's a port index
            return self._midi.openPort(port)
    
    def close_port(self):
        """Close the port"""
        return self._midi.closePort()
    
    def set_callback(self, callback):
        """Set MIDI callback"""
        return self._midi.setCallback(callback)
    
    def ignore_types(self, sysex=False, timing=True, active_sense=True):
        """Set ignored MIDI types"""
        return self._midi.ignoreTypes(sysex, timing, active_sense)
    
    def send_message(self, message):
        """Send MIDI message (for compatibility)"""
        # This is typically not used on input, but included for compatibility
        pass


class MidiOut:
    """Compatibility wrapper for RtMidiOut"""
    
    def __init__(self):
        self._midi = rtmidi.RtMidiOut()
    
    def get_ports(self):
        """Get list of available output ports"""
        ports = []
        for i in range(self._midi.getPortCount()):
            ports.append(self._midi.getPortName(i))
        return ports
    
    def is_port_open(self):
        """Check if port is open"""
        return self._midi.isPortOpen()
    
    def open_port(self, port):
        """Open port by name or index"""
        if isinstance(port, str):
            # Find port by name
            for i in range(self._midi.getPortCount()):
                if self._midi.getPortName(i) == port:
                    return self._midi.openPort(i)
            raise ValueError(f"Port '{port}' not found")
        else:
            # Assume it's a port index
            return self._midi.openPort(port)
    
    def close_port(self):
        """Close the port"""
        return self._midi.closePort()
    
    def send_message(self, message):
        """Send MIDI message"""
        return self._midi.sendMessage(message)

# Create aliases for compatibility with existing codebase
rtmidi.MidiIn = MidiIn
rtmidi.MidiOut = MidiOut
