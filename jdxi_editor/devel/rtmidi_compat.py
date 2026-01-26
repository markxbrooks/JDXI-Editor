"""
rtmidi Compatibility Module

This module provides compatibility between different versions of rtmidi.
It creates wrapper classes that match the older MidiIn/MidiOut API expected by the JD-Xi Editor codebase.
"""

import rtmidi

# Store original rtmidi classes before we potentially overwrite them
_original_rtmidi_in = getattr(rtmidi, 'RtMidiIn', None)
_original_rtmidi_out = getattr(rtmidi, 'RtMidiOut', None)
_original_midi_in = getattr(rtmidi, 'MidiIn', None)
_original_midi_out = getattr(rtmidi, 'MidiOut', None)


class MidiIn:
    """Compatibility wrapper for RtMidiIn"""
    
    def __init__(self):
        # Try to use the original rtmidi classes (before we overwrote them)
        if _original_rtmidi_in is not None:
            try:
                self._midi = _original_rtmidi_in()
            except (AttributeError, TypeError):
                self._midi = self._create_mock()
        elif _original_midi_in is not None and _original_midi_in is not MidiIn:
            try:
                self._midi = _original_midi_in()
            except (AttributeError, TypeError):
                self._midi = self._create_mock()
        else:
            # Fallback: create a mock for testing
            self._midi = self._create_mock()
    
    @staticmethod
    def _create_mock():
        """Create a mock MidiIn for testing"""
        class MockMidiIn:
            def getPortCount(self): return 0
            def getPortName(self, i): return ""
            def isPortOpen(self): return False
            def openPort(self, port): pass
            def closePort(self): pass
            def setCallback(self, callback): pass
            def ignoreTypes(self, sysex, timing, active_sense): pass
        return MockMidiIn()
    
    def get_ports(self):
        """Get list of available input ports"""
        # Handle both old API (getPortCount/getPortName) and new API (get_port_count/get_port_name)
        if hasattr(self._midi, 'get_port_count'):
            ports = []
            for i in range(self._midi.get_port_count()):
                ports.append(self._midi.get_port_name(i))
            return ports
        elif hasattr(self._midi, 'getPortCount'):
            ports = []
            for i in range(self._midi.getPortCount()):
                ports.append(self._midi.getPortName(i))
            return ports
        else:
            return []
    
    def is_port_open(self):
        """Check if port is open"""
        if hasattr(self._midi, 'is_port_open'):
            return self._midi.is_port_open()
        elif hasattr(self._midi, 'isPortOpen'):
            return self._midi.isPortOpen()
        else:
            return False
    
    def open_port(self, port):
        """Open port by name or index"""
        if isinstance(port, str):
            # Find port by name
            if hasattr(self._midi, 'get_port_count'):
                for i in range(self._midi.get_port_count()):
                    if self._midi.get_port_name(i) == port:
                        return self._midi.open_port(i)
            elif hasattr(self._midi, 'getPortCount'):
                for i in range(self._midi.getPortCount()):
                    if self._midi.getPortName(i) == port:
                        return self._midi.openPort(i)
            raise ValueError(f"Port '{port}' not found")
        else:
            # Assume it's a port index
            if hasattr(self._midi, 'open_port'):
                return self._midi.open_port(port)
            elif hasattr(self._midi, 'openPort'):
                return self._midi.openPort(port)
            else:
                pass
    
    def close_port(self):
        """Close the port"""
        if hasattr(self._midi, 'close_port'):
            return self._midi.close_port()
        elif hasattr(self._midi, 'closePort'):
            return self._midi.closePort()
        else:
            pass
    
    def set_callback(self, callback):
        """Set MIDI callback"""
        # Handle both old API (setCallback) and new API (set_callback)
        if hasattr(self._midi, 'set_callback'):
            return self._midi.set_callback(callback)
        elif hasattr(self._midi, 'setCallback'):
            return self._midi.setCallback(callback)
        else:
            # Mock doesn't need to do anything
            pass
    
    def ignore_types(self, sysex=False, timing=True, active_sense=True):
        """Set ignored MIDI types"""
        # Handle both old API (ignoreTypes) and new API (ignore_types)
        if hasattr(self._midi, 'ignore_types'):
            return self._midi.ignore_types(sysex, timing, active_sense)
        elif hasattr(self._midi, 'ignoreTypes'):
            return self._midi.ignoreTypes(sysex, timing, active_sense)
        else:
            # Mock doesn't need to do anything
            pass
    
    def send_message(self, message):
        """Send MIDI message (for compatibility)"""
        # This is typically not used on input, but included for compatibility
        pass


class MidiOut:
    """Compatibility wrapper for RtMidiOut"""
    
    def __init__(self):
        # Try to use the original rtmidi classes (before we overwrote them)
        if _original_rtmidi_out is not None:
            try:
                self._midi = _original_rtmidi_out()
            except (AttributeError, TypeError):
                self._midi = self._create_mock()
        elif _original_midi_out is not None and _original_midi_out is not MidiOut:
            try:
                self._midi = _original_midi_out()
            except (AttributeError, TypeError):
                self._midi = self._create_mock()
        else:
            # Fallback: create a mock for testing
            self._midi = self._create_mock()
    
    @staticmethod
    def _create_mock():
        """Create a mock MidiOut for testing"""
        class MockMidiOut:
            def getPortCount(self): return 0
            def getPortName(self, i): return ""
            def isPortOpen(self): return False
            def openPort(self, port): pass
            def closePort(self): pass
            def sendMessage(self, message): pass
            def send_message(self, message): pass  # Alternative method name
        return MockMidiOut()
    
    def get_ports(self):
        """Get list of available output ports"""
        # Handle both old API (getPortCount/getPortName) and new API (get_port_count/get_port_name)
        if hasattr(self._midi, 'get_port_count'):
            ports = []
            for i in range(self._midi.get_port_count()):
                ports.append(self._midi.get_port_name(i))
            return ports
        elif hasattr(self._midi, 'getPortCount'):
            ports = []
            for i in range(self._midi.getPortCount()):
                ports.append(self._midi.getPortName(i))
            return ports
        else:
            return []
    
    def is_port_open(self):
        """Check if port is open"""
        if hasattr(self._midi, 'is_port_open'):
            return self._midi.is_port_open()
        elif hasattr(self._midi, 'isPortOpen'):
            return self._midi.isPortOpen()
        else:
            return False
    
    def open_port(self, port):
        """Open port by name or index"""
        if isinstance(port, str):
            # Find port by name
            if hasattr(self._midi, 'get_port_count'):
                for i in range(self._midi.get_port_count()):
                    if self._midi.get_port_name(i) == port:
                        return self._midi.open_port(i)
            elif hasattr(self._midi, 'getPortCount'):
                for i in range(self._midi.getPortCount()):
                    if self._midi.getPortName(i) == port:
                        return self._midi.openPort(i)
            raise ValueError(f"Port '{port}' not found")
        else:
            # Assume it's a port index
            if hasattr(self._midi, 'open_port'):
                return self._midi.open_port(port)
            elif hasattr(self._midi, 'openPort'):
                return self._midi.openPort(port)
            else:
                pass
    
    def close_port(self):
        """Close the port"""
        if hasattr(self._midi, 'close_port'):
            return self._midi.close_port()
        elif hasattr(self._midi, 'closePort'):
            return self._midi.closePort()
        else:
            pass
    
    def send_message(self, message):
        """Send MIDI message"""
        if hasattr(self._midi, 'sendMessage'):
            return self._midi.sendMessage(message)
        elif hasattr(self._midi, 'send_message'):
            return self._midi.send_message(message)
        else:
            pass  # Mock doesn't need to do anything

# Create aliases for compatibility with existing codebase
# Only assign if they don't already exist to avoid recursion
if not hasattr(rtmidi, 'MidiIn') or (hasattr(rtmidi, 'MidiIn') and rtmidi.MidiIn is not MidiIn):
    rtmidi.MidiIn = MidiIn
if not hasattr(rtmidi, 'MidiOut') or (hasattr(rtmidi, 'MidiOut') and rtmidi.MidiOut is not MidiOut):
    rtmidi.MidiOut = MidiOut
