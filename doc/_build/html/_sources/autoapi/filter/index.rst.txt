filter
======

.. py:module:: filter

.. autoapi-nested-parse::

   PWM Widget
   ==========

   This widget provides a user interface for controlling Pulse Width Modulation (PWM) parameters,
   with a graphical plot to visualize the modulation envelope.
   It includes controls for pulse width and modulation depth,
   and can communicate with MIDI devices.



Classes
-------

.. autoapisummary::

   filter.FilterWidget


Module Contents
---------------

.. py:class:: FilterWidget(cutoff_param: jdxi_editor.midi.data.parameter.AddressParameter, slope_param: jdxi_editor.midi.data.parameter.AddressParameter = None, midi_helper: Optional[jdxi_editor.midi.io.helper.MidiIOHelper] = None, controls: dict[jdxi_editor.midi.data.parameter.AddressParameter, PySide6.QtWidgets.QWidget] = None, address: Optional[jdxi_editor.midi.data.address.address.RolandSysExAddress] = None, create_parameter_slider: Callable = None, create_parameter_switch: Callable = None, parent: Optional[PySide6.QtWidgets.QWidget] = None)

   Bases: :py:obj:`jdxi_editor.ui.widgets.envelope.base.EnvelopeWidgetBase`


   Base class for envelope widgets in the JD-Xi editor


   .. py:attribute:: slope_param_changed


   .. py:attribute:: cutoff_param_changed


   .. py:attribute:: envelope_changed


   .. py:attribute:: plot
      :value: None



   .. py:attribute:: parent
      :value: None



   .. py:attribute:: address
      :value: None



   .. py:attribute:: midi_helper
      :value: None



   .. py:attribute:: _create_parameter_slider
      :value: None



   .. py:attribute:: _create_parameter_switch
      :value: None



   .. py:attribute:: envelope


   .. py:attribute:: cutoff_param_control


   .. py:attribute:: _control_widgets


   .. py:attribute:: horizontal_layout


   .. py:attribute:: controls_vertical_layout


   .. py:method:: on_envelope_changed(envelope: dict) -> None

      Handle envelope changes from controls

      :param envelope: dict
      :return: None



   .. py:method:: on_cutoff_param_changed(val: int) -> None

      Handle pulse width changes from slider

      :param val: int
      :return: None



   .. py:method:: on_slope_param_changed(val: int) -> None

      Handle modulation depth changes from slider

      :param val: int
      :return: None



   .. py:method:: update_envelope_from_slider(slider: PySide6.QtWidgets.QSlider) -> None

      Update envelope with value from a single slider



   .. py:method:: update_envelope_from_controls() -> None

      Update envelope values from slider controls



   .. py:method:: update_controls_from_envelope() -> None

      Update slider controls from envelope values.



