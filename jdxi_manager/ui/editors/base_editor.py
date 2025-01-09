from PySide6.QtWidgets import QMainWindow
import logging

class BaseEditor(QMainWindow):
    def _update_main_window_preset(self, preset_num, preset_name):
        """Update main window preset display"""
        if self.main_window:
            self.main_window.update_preset_display(preset_num, preset_name)
            
    def _handle_program_change(self, program_number):
        """Handle program change from device"""
        try:
            preset_num = program_number + 1  # Convert 0-based to 1-based
            # Request patch name from device
            self._request_patch_name(preset_num)
            logging.debug(f"Received program change: {preset_num}")
            
        except Exception as e:
            logging.error(f"Error handling program change: {str(e)}")
            
    def _request_patch_name(self, preset_num):
        """Request patch name from device"""
        raise NotImplementedError("Subclasses must implement _request_patch_name") 