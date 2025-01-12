from PySide6.QtWidgets import QMainWindow, QWidget
from typing import Optional
import logging

from jdxi_manager.midi import MIDIHelper
from jdxi_manager.midi.messages import JDXiSysEx
from jdxi_manager.midi.constants import START_OF_SYSEX, END_OF_SYSEX

class BaseEditor(QMainWindow):
    """Base class for synth editors"""
    
    def __init__(self, midi_helper: Optional[MIDIHelper] = None, parent: Optional[QWidget] = None):
        """Initialize base editor
        
        Args:
            midi_helper: MIDI helper instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.main_window = parent
        
    def _request_patch_data(self):
        """Request current patch data from synth
        
        This method should be overridden by child classes to implement
        specific parameter request logic.
        """
        try:
            if not hasattr(self, 'area') or not hasattr(self, 'part'):
                logging.warning("Editor must define 'area' and 'part' attributes")
                return
                
            msg = JDXiSysEx.create_parameter_request(
                area=self.area,
                part=self.part,
                group=self.group if hasattr(self, 'group') else 0x00,
                param=self.start_param if hasattr(self, 'start_param') else 0x00,
                size=self.param_size if hasattr(self, 'param_size') else 0x100
            )
            
            if self.midi_helper:
                self.midi_helper.send_message(msg)
                logging.debug(f"Requested patch data for {self.__class__.__name__}")
            else:
                logging.warning("No MIDI helper available - cannot request patch data")
                
        except Exception as e:
            logging.error(f"Error requesting patch data: {str(e)}")
            
    def _handle_midi_input(self, msg):
        """Handle incoming MIDI messages
        
        This method provides basic SysEx handling and should be extended
        by child classes for specific parameter handling.
        """
        try:
            # Check if it's a SysEx message
            if msg[0] == START_OF_SYSEX and msg[-1] == END_OF_SYSEX:
                # Extract address and data
                addr = msg[8:12]  # 4 bytes of address
                data = msg[12:-2]  # Data bytes (excluding checksum and end of sysex)
                
                # Update UI based on received data
                self._update_ui_from_sysex(addr, data)
                logging.debug(f"Received patch data: addr={[hex(b) for b in addr]}, data={[hex(b) for b in data]}")
                
        except Exception as e:
            logging.error(f"Error handling MIDI input: {str(e)}")
            
    def _update_ui_from_sysex(self, addr, data):
        """Update UI controls based on received SysEx data
        
        This method should be overridden by child classes to implement
        specific UI update logic.
        
        Args:
            addr: 4-byte address from SysEx message
            data: Parameter data bytes
        """
        pass  # To be implemented by child classes 