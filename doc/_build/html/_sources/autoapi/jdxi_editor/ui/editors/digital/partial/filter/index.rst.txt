jdxi_editor.ui.editors.digital.partial.filter
=============================================

.. py:module:: jdxi_editor.ui.editors.digital.partial.filter

.. autoapi-nested-parse::

   Digital Filter Section for the JDXI Editor



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.digital.partial.filter.DigitalFilterSection


Module Contents
---------------

.. py:class:: DigitalFilterSection(create_parameter_slider: Callable, create_parameter_switch: Callable, partial_number: int, midi_helper: jdxi_editor.midi.io.helper.MidiIOHelper, controls: dict, address: jdxi_editor.midi.data.address.address.RolandSysExAddress)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Filter section for the digital partial editor.


   .. py:attribute:: partial_number


   .. py:attribute:: midi_helper


   .. py:attribute:: controls


   .. py:attribute:: address


   .. py:attribute:: _create_parameter_slider


   .. py:attribute:: _create_parameter_switch


   .. py:method:: setup_ui()

      Set up the UI for the filter section.



   .. py:method:: _on_filter_mode_changed(mode: int)

      Handle filter mode changes



   .. py:method:: update_filter_controls_state(mode: int)

      Update filter controls enabled state based on mode



