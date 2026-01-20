from typing import Dict, Optional

from PySide6.QtCore import QObject

from decologr import Decologr as log
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParam
from picomidi.sysex.parameter.address import AddressParameter


class PartialController(QObject):
    """
    A mixin for managing partial controls in the digital synth editor.
    Provides methods for enabling/disabling partials, updating parameters,
    and handling state changes for partials.
    """

    def __init__(self, partial_count: int = 3, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.partial_states = {
            i: {"enabled": False, "selected": False}
            for i in range(1, partial_count + 1)
        }
        self.partial_controls: Dict[int, dict] = (
            {}
        )  # Controls for each partial (e.g., sliders, switches)

    def enable_partial(self, partial_number: int, enabled: bool = True) -> None:
        """
        Enable or disable a specific partial.

        :param partial_number: The partial number to enable/disable.
        :param enabled: True to enable, False to disable.
        """
        if partial_number in self.partial_states:
            self.partial_states[partial_number]["enabled"] = enabled
            # Update UI or send MIDI message here if needed
            self._update_partial_state_ui(partial_number)

    def select_partial(self, partial_number: int) -> None:
        """
        Select a specific partial. Deselects others.

        :param partial_number: The partial number to select.
        """
        for num in self.partial_states.keys():
            self.partial_states[num]["selected"] = num == partial_number
            self._update_partial_state_ui(num)

    def update_partial_parameter(
        self, partial_number: int, param: str, value: int
    ) -> None:
        """
        Update a parameter for a specific partial.

        :param partial_number: The partial number.
        :param param: The parameter name to update.
        :param value: The value to set.
        """
        if (
            partial_number in self.partial_states
            and partial_number in self.partial_controls
        ):
            control = self.partial_controls[partial_number].get(param)
            if control:
                control.blockSignals(True)
                control.setValue(
                    value
                )  # Update slider or UI element without triggering MIDI send
                control.blockSignals(False)
                # Log parameter change
                self._log_partial_parameter_change(partial_number, param, value)

    def _update_partial_state_ui(self, partial_number: int) -> None:
        """
        Update the UI for the state of a specific partial.

        :param partial_number: The partial number to update.
        """
        state = self.partial_states[partial_number]
        print(
            f"Updating UI for Partial {partial_number}: Enabled={state['enabled']}, Selected={state['selected']}"
        )

    def _log_partial_parameter_change(
        self, partial_number: int, param: str, value: int
    ) -> None:
        """
        Log a parameter change for a specific partial.

        :param partial_number: The partial number.
        :param param: The parameter name.
        :param value: The new value.
        """
        print(f"Partial {partial_number}: {param} set to {value}")

    def _on_partial_state_changed(
        self, partial: DigitalPartialParam, enabled: bool, selected: bool
    ) -> None:
        """
        Handle the state change of a partial (enabled/disabled and selected/unselected).

        :param partial: The partial to modify
        :param enabled: Whether the partial is enabled (ON/OFF)
        :param selected: Whether the partial is selected
        :return: None
        """
        self.set_partial_state(partial, enabled, selected)

        # Enable/disable corresponding tab
        partial_num = partial.value
        self.partial_tab_widget.setTabEnabled(partial_num - 1, enabled)

        # Switch to selected partial's tab
        if selected:
            self.partial_tab_widget.setCurrentIndex(partial_num - 1)

    def set_partial_state(
        self, partial: DigitalPartialParam, enabled: bool = True, selected: bool = True
    ) -> Optional[bool]:
        """
        Set the state of a partial (enabled/disabled and selected/unselected).

        :param partial: The partial to modify
        :param enabled: Whether the partial is enabled (ON/OFF)
        :param selected: Whether the partial is selected
        :return: True if successful, False otherwise
        """
        try:
            log.parameter("Setting partial:", partial.switch_param)
            log.parameter("Partial state enabled (Yes/No):", enabled)
            log.parameter("Partial selected (Yes/No):", selected)
            self.send_midi_parameter(
                param=partial.switch_param, value=1 if enabled else 0
            )
            self.send_midi_parameter(
                param=partial.select_param, value=1 if selected else 0
            )
            return True
        except Exception as ex:
            log.error(f"Error setting partial {partial.name} state: {str(ex)}")
            return False

    def _initialize_partial_states(self):
        """
        Initialize partial states with defaults
        Default: Partial 1 enabled and selected, others disabled
        """
        for partial in DigitalPartialParam.get_partials():
            enabled = partial == DigitalPartialParam.PARTIAL_1
            selected = enabled
            self.partials_panel.switches[partial].setState(enabled, selected)
            self.partial_tab_widget.setTabEnabled(partial.STATUS - 1, enabled)
        self.partial_tab_widget.setCurrentIndex(0)

    def _handle_special_params(
        self, partial_no: int, param: AddressParameter, value: int
    ) -> None:
        """
        Handle special parameters that require additional UI updates.

        :param partial_no: int
        :param param: AddressParameter
        :param value: int
        :return: None
        """
        if param == DigitalPartialParam.OSC_WAVE:
            self._update_waveform_buttons(partial_no, value)
            log.parameter("Updated waveform buttons for OSC_WAVE", value)

        elif param == DigitalPartialParam.FILTER_MODE_SWITCH:
            self.partial_editors[partial_no].filter_mode_switch.blockSignals(True)
            self.partial_editors[partial_no].filter_mode_switch.setValue(value)
            self.partial_editors[partial_no].filter_mode_switch.blockSignals(False)
            self._update_filter_state(partial_no, value)
            log.parameter("Updated filter state for FILTER_MODE_SWITCH", value)

    def _apply_partial_ui_updates(self, partial_no: int, sysex_data: dict) -> None:
        """
        Apply updates to the UI components based on the received SysEx data.

        :param partial_no: int
        :param sysex_data: dict
        :return: None
        """
        successes, failures = [], []

        for param_name, param_value in sysex_data.items():
            param = DigitalPartialParam.get_by_name(param_name)
            if not param:
                failures.append(param_name)
                continue

            if param == DigitalPartialParam.OSC_WAVE:
                self._update_waveform_buttons(partial_no, param_value)
            elif param == DigitalPartialParam.FILTER_MODE_SWITCH:
                self._update_filter_state(partial_no, value=param_value)
            elif param in [
                DigitalPartialParam.AMP_ENV_ATTACK_TIME,
                DigitalPartialParam.AMP_ENV_DECAY_TIME,
                DigitalPartialParam.AMP_ENV_SUSTAIN_LEVEL,
                DigitalPartialParam.AMP_ENV_RELEASE_TIME,
                DigitalPartialParam.FILTER_ENV_ATTACK_TIME,
                DigitalPartialParam.FILTER_ENV_DECAY_TIME,
                DigitalPartialParam.FILTER_ENV_SUSTAIN_LEVEL,
                DigitalPartialParam.FILTER_ENV_RELEASE_TIME,
            ]:
                self._update_partial_adsr_widgets(
                    partial_no, param, param_value, successes, failures
                )
            elif param in [
                DigitalPartialParam.OSC_PITCH_ENV_ATTACK_TIME,
                DigitalPartialParam.OSC_PITCH_ENV_DECAY_TIME,
                DigitalPartialParam.OSC_PITCH_ENV_DEPTH,
            ]:
                self._update_partial_pitch_env_widgets(
                    partial_no, param, param_value, successes, failures
                )
            else:
                self._update_partial_slider(
                    partial_no, param, param_value, successes, failures
                )

        log.debug_info(successes, failures)

    def _update_waveform_buttons(self, partial_no, param_value):
        pass
