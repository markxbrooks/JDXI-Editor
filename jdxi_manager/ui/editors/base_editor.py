from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtCore import Qt
import logging

from jdxi_manager.midi.messages import (
    create_parameter_message,
    create_sysex_message,
    create_patch_load_message,
    create_patch_save_message
)
from jdxi_manager.midi.constants import (
    START_OF_SYSEX, END_OF_SYSEX,
    ROLAND_ID, DEVICE_ID, MODEL_ID_1, MODEL_ID_2,
    MODEL_ID, JD_XI_ID, DT1_COMMAND_12
)

class BaseEditor(QMainWindow):
    """Base class for all synth editors providing common MIDI functionality"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.midi_helper = None
        self.current_preset_num = 1
        self.current_preset_name = "INIT PATCH"
        
    def set_midi_helper(self, midi_helper):
        """Set MIDI helper instance"""
        self.midi_helper = midi_helper
        
    def _send_parameter(self, area: int, param: int, value: int):
        """Send parameter change to device
        
        Args:
            area: Memory area (e.g. DIGITAL_SYNTH_AREA)
            param: Parameter number
            value: Parameter value
        """
        try:
            msg = create_parameter_message(area, 0x00, param, value)
            if self.midi_helper:
                self.midi_helper.send_message(msg)
                # Blink MIDI out indicator if available
                if self.main_window and hasattr(self.main_window, 'midi_out_indicator'):
                    self.main_window.midi_out_indicator.blink()
                logging.debug(f"Sent parameter: area={hex(area)} param={hex(param)} value={value}")
        except Exception as e:
            logging.error(f"Error sending parameter: {str(e)}")
            
    def _send_sysex(self, address: bytes, data: bytes):
        """Send SysEx message to device
        
        Args:
            address: Address bytes
            data: Data bytes
        """
        try:
            msg = create_sysex_message(address, data)
            if self.midi_helper:
                self.midi_helper.send_message(msg)
                # Blink MIDI out indicator if available
                if self.main_window and hasattr(self.main_window, 'midi_out_indicator'):
                    self.main_window.midi_out_indicator.blink()
                logging.debug(f"Sent SysEx: addr={address.hex()} data={data.hex()}")
        except Exception as e:
            logging.error(f"Error sending SysEx: {str(e)}")
            
    def _handle_midi_message(self, message, timestamp):
        """Handle incoming MIDI message
        
        Args:
            message: MIDI message bytes
            timestamp: Message timestamp
        """
        try:
            data = message[0]  # Get raw MIDI data
            
            # Blink MIDI in indicator if available
            if self.main_window and hasattr(self.main_window, 'midi_in_indicator'):
                self.main_window.midi_in_indicator.blink()
            
            # Check if it's a SysEx message for this device
            if (data[0] == START_OF_SYSEX and 
                data[1] == ROLAND_ID and
                data[4:8] == bytes([MODEL_ID_1, MODEL_ID_2, MODEL_ID, JD_XI_ID])):
                
                # Extract address and data
                addr = data[8:12]  # 4 bytes of address
                param_data = data[12:-1]  # Parameter data (excluding F7)
                
                # Update UI based on received data
                self._update_ui_from_sysex(addr, param_data)
                
        except Exception as e:
            logging.error(f"Error handling MIDI message: {str(e)}")
            
    def _update_ui_from_sysex(self, addr: bytes, data: bytes):
        """Update UI based on received SysEx data
        
        Args:
            addr: Address bytes
            data: Data bytes
            
        Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement _update_ui_from_sysex")
            
    def _update_main_window_preset(self, preset_num: int, preset_name: str):
        """Update main window preset display"""
        if self.main_window:
            self.main_window.update_preset_display(preset_num, preset_name)
            
    def _handle_program_change(self, program_number: int):
        """Handle program change from device"""
        try:
            preset_num = program_number + 1  # Convert 0-based to 1-based
            # Request patch name from device
            self._request_patch_name(preset_num)
            logging.debug(f"Received program change: {preset_num}")
            
        except Exception as e:
            logging.error(f"Error handling program change: {str(e)}")
            
    def _request_patch_data(self):
        """Request current patch data from device
        
        Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement _request_patch_data")
            
    def _request_patch_name(self, preset_num: int):
        """Request patch name from device
        
        Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement _request_patch_name")

    def closeEvent(self, event):
        """Handle window close event"""
        self.save_window_state()
        event.accept()
        
    def save_window_state(self):
        """Save window position and size"""
        if self.main_window and hasattr(self.main_window, 'settings'):
            settings = self.main_window.settings
            settings.beginGroup(self.__class__.__name__)
            settings.setValue("geometry", self.saveGeometry())
            settings.setValue("state", self.saveState())
            settings.endGroup()
            
    def restore_window_state(self):
        """Restore saved window position and size"""
        if self.main_window and hasattr(self.main_window, 'settings'):
            settings = self.main_window.settings
            settings.beginGroup(self.__class__.__name__)
            geometry = settings.value("geometry")
            state = settings.value("state")
            if geometry:
                self.restoreGeometry(geometry)
            if state:
                self.restoreState(state)
            settings.endGroup()

    def show_error(self, title: str, message: str):
        """Show error message box"""
        QMessageBox.critical(self, title, message)
        
    def show_warning(self, title: str, message: str):
        """Show warning message box"""
        QMessageBox.warning(self, title, message)
        
    def show_info(self, title: str, message: str):
        """Show info message box"""
        QMessageBox.information(self, title, message)

    def load_preset(self, preset_num: int):
        """Load a preset by number"""
        try:
            msg = create_patch_load_message(preset_num)
            if self.midi_helper:
                self.midi_helper.send_message(msg)
                self.current_preset_num = preset_num
                self._request_patch_name(preset_num)
                logging.debug(f"Loading preset {preset_num}")
        except Exception as e:
            logging.error(f"Error loading preset: {str(e)}")
            
    def save_preset(self, preset_num: int):
        """Save current settings to preset number"""
        try:
            msg = create_patch_save_message(preset_num)
            if self.midi_helper:
                self.midi_helper.send_message(msg)
                self.current_preset_num = preset_num
                logging.debug(f"Saving preset {preset_num}")
        except Exception as e:
            logging.error(f"Error saving preset: {str(e)}")

    def handle_midi_error(self, error: Exception):
        """Handle MIDI errors consistently"""
        error_msg = str(error)
        logging.error(f"MIDI Error: {error_msg}")
        self.show_error("MIDI Error", error_msg)

    def validate_midi_value(self, value: int, min_val: int = 0, max_val: int = 127) -> bool:
        """Validate MIDI value is in range"""
        return min_val <= value <= max_val

    def validate_preset_number(self, preset_num: int) -> bool:
        """Validate preset number is valid"""
        return 1 <= preset_num <= 128

    def set_window_title(self, title: str):
        """Set window title with current preset info"""
        self.setWindowTitle(f"{title} - {self.current_preset_num:03d}:{self.current_preset_name}")

    def update_preset_info(self, preset_num: int, preset_name: str):
        """Update preset information"""
        self.current_preset_num = preset_num
        self.current_preset_name = preset_name
        self._update_main_window_preset(preset_num, preset_name)
        self.set_window_title(self.__class__.__name__.replace("Editor", ""))

    def create_backup(self):
        """Request all patch data for backup"""
        try:
            self._request_patch_data()
            logging.info("Backup requested")
        except Exception as e:
            logging.error(f"Error creating backup: {str(e)}")
            self.show_error("Backup Error", str(e))

    def restore_backup(self, data: bytes):
        """Restore patch data from backup"""
        try:
            # Send data back to device
            if self.midi_helper:
                self.midi_helper.send_message(data)
                logging.info("Backup restored")
        except Exception as e:
            logging.error(f"Error restoring backup: {str(e)}")
            self.show_error("Restore Error", str(e)) 