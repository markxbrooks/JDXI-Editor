jdxi_editor.ui.editors.analog.filter
====================================

.. py:module:: jdxi_editor.ui.editors.analog.filter

.. autoapi-nested-parse::

   Analog Filter Section



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.analog.filter.AnalogFilterSection


Module Contents
---------------

.. py:class:: AnalogFilterSection(create_parameter_slider: Callable, create_parameter_switch: Callable, on_filter_mode_changed: Callable, send_control_change: Callable, midi_helper: jdxi_editor.midi.io.helper.MidiIOHelper, controls: dict[jdxi_editor.midi.data.parameter.AddressParameter, PySide6.QtWidgets.QWidget], address: jdxi_editor.midi.data.address.address.RolandSysExAddress)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Analog Filter Section


   .. py:attribute:: filter_resonance
      :value: None



   .. py:attribute:: _create_parameter_slider


   .. py:attribute:: _create_parameter_switch


   .. py:attribute:: _on_filter_mode_changed


   .. py:attribute:: send_control_change


   .. py:attribute:: midi_helper


   .. py:attribute:: address


   .. py:attribute:: controls


   .. py:method:: init_ui()

      Initialize the UI



