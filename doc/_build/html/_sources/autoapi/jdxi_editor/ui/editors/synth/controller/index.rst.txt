jdxi_editor.ui.editors.synth.controller
=======================================

.. py:module:: jdxi_editor.ui.editors.synth.controller


Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.synth.controller.PartialController


Module Contents
---------------

.. py:class:: PartialController(partial_count: int = 3, parent: Optional[PySide6.QtCore.QObject] = None)

   Bases: :py:obj:`PySide6.QtCore.QObject`


   A mixin for managing partial controls in the digital synth editor.
   Provides methods for enabling/disabling partials, updating parameters,
   and handling state changes for partials.


   .. py:attribute:: partial_states


   .. py:attribute:: partial_controls
      :type:  Dict[int, dict]


   .. py:method:: enable_partial(partial_number: int, enabled: bool = True) -> None

      Enable or disable a specific partial.

      :param partial_number: The partial number to enable/disable.
      :param enabled: True to enable, False to disable.



   .. py:method:: select_partial(partial_number: int) -> None

      Select a specific partial. Deselects others.

      :param partial_number: The partial number to select.



   .. py:method:: update_partial_parameter(partial_number: int, param: str, value: int) -> None

      Update a parameter for a specific partial.

      :param partial_number: The partial number.
      :param param: The parameter name to update.
      :param value: The value to set.



   .. py:method:: _update_partial_state_ui(partial_number: int) -> None

      Update the UI for the state of a specific partial.

      :param partial_number: The partial number to update.



   .. py:method:: _log_partial_parameter_change(partial_number: int, param: str, value: int) -> None

      Log a parameter change for a specific partial.

      :param partial_number: The partial number.
      :param param: The parameter name.
      :param value: The new value.



   .. py:method:: _on_partial_state_changed(partial: jdxi_editor.midi.data.digital.partial.DigitalPartial, enabled: bool, selected: bool) -> None

      Handle the state change of a partial (enabled/disabled and selected/unselected).

      :param partial: The partial to modify
      :param enabled: Whether the partial is enabled (ON/OFF)
      :param selected: Whether the partial is selected
      :return: None



   .. py:method:: set_partial_state(partial: jdxi_editor.midi.data.digital.partial.DigitalPartial, enabled: bool = True, selected: bool = True) -> Optional[bool]

      Set the state of a partial (enabled/disabled and selected/unselected).

      :param partial: The partial to modify
      :param enabled: Whether the partial is enabled (ON/OFF)
      :param selected: Whether the partial is selected
      :return: True if successful, False otherwise



   .. py:method:: _initialize_partial_states()

      Initialize partial states with defaults
      Default: Partial 1 enabled and selected, others disabled



   .. py:method:: _handle_special_params(partial_no: int, param: jdxi_editor.midi.data.parameter.synth.AddressParameter, value: int) -> None

      Handle special parameters that require additional UI updates.

      :param partial_no: int
      :param param: AddressParameter
      :param value: int
      :return: None



   .. py:method:: _apply_partial_ui_updates(partial_no: int, sysex_data: dict) -> None

      Apply updates to the UI components based on the received SysEx data.

      :param partial_no: int
      :param sysex_data: dict
      :return: None



   .. py:method:: _update_waveform_buttons(partial_no, param_value)


