from typing import Dict, Optional
from PySide6.QtCore import QObject

class PartialController(QObject):
    """
    A mixin for managing partial controls in the digital synth editor.
    Provides methods for enabling/disabling partials, updating parameters,
    and handling state changes for partials.
    """

    def __init__(self, partial_count: int = 3, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.partial_states = {i: {'enabled': False, 'selected': False} for i in range(1, partial_count + 1)}
        self.partial_controls: Dict[int, dict] = {}  # Controls for each partial (e.g., sliders, switches)

    def enable_partial(self, partial_number: int, enabled: bool = True) -> None:
        """
        Enable or disable a specific partial.
        :param partial_number: The partial number to enable/disable.
        :param enabled: True to enable, False to disable.
        """
        if partial_number in self.partial_states:
            self.partial_states[partial_number]['enabled'] = enabled
            # Update UI or send MIDI message here if needed
            self._update_partial_state_ui(partial_number)

    def select_partial(self, partial_number: int) -> None:
        """
        Select a specific partial. Deselects others.
        :param partial_number: The partial number to select.
        """
        for num in self.partial_states.keys():
            self.partial_states[num]['selected'] = (num == partial_number)
            self._update_partial_state_ui(num)

    def update_partial_parameter(self, partial_number: int, param: str, value: int) -> None:
        """
        Update a parameter for a specific partial.
        :param partial_number: The partial number.
        :param param: The parameter name to update.
        :param value: The value to set.
        """
        if partial_number in self.partial_states and partial_number in self.partial_controls:
            control = self.partial_controls[partial_number].get(param)
            if control:
                control.setValue(value)  # Example: Update slider or UI element
                # Send MIDI message or log parameter change if needed
                self._log_partial_parameter_change(partial_number, param, value)

    def _update_partial_state_ui(self, partial_number: int) -> None:
        """
        Update the UI for the state of a specific partial.
        :param partial_number: The partial number to update.
        """
        state = self.partial_states[partial_number]
        print(f"Updating UI for Partial {partial_number}: Enabled={state['enabled']}, Selected={state['selected']}")

    def _log_partial_parameter_change(self, partial_number: int, param: str, value: int) -> None:
        """
        Log a parameter change for a specific partial.
        :param partial_number: The partial number.
        :param param: The parameter name.
        :param value: The new value.
        """
        print(f"Partial {partial_number}: {param} set to {value}")