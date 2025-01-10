import logging
from typing import Optional
import rtmidi

class MIDIConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MIDIConnection, cls).__new__(cls)
            cls._instance._midi_in = None
            cls._instance._midi_out = None
            cls._instance._main_window = None
        return cls._instance
    
    @property
    def midi_in(self):
        return self._midi_in
        
    @property
    def midi_out(self):
        return self._midi_out
        
    def initialize(self, midi_in, midi_out, main_window=None):
        """Initialize MIDI connections"""
        self._midi_in = midi_in
        self._midi_out = midi_out
        self._main_window = main_window
        logging.debug("MIDI Connection singleton initialized")
        
    def send_message(self, message):
        """Send MIDI message and trigger indicator"""
        try:
            if self._midi_out:
                self._midi_out.send_message(message)
                # Blink indicator if main window exists
                if self._main_window and hasattr(self._main_window, 'midi_out_indicator'):
                    self._main_window.midi_out_indicator.blink()
                logging.debug(f"Sent MIDI message: {' '.join([hex(b)[2:].upper().zfill(2) for b in message])}")
            else:
                logging.warning("No MIDI output port available")
                
        except Exception as e:
            logging.error(f"Error sending MIDI message: {str(e)}")
                
    def set_input_callback(self, callback):
        """Set MIDI input callback"""
        if self._midi_in:
            self._midi_in.set_callback(callback)
            logging.debug("MIDI input callback set")
        else:
            logging.warning("No MIDI input port available") 