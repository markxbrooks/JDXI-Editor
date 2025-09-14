jdxi_editor.ui.editors.analog.amp
=================================

.. py:module:: jdxi_editor.ui.editors.analog.amp

.. autoapi-nested-parse::

   Amp section of the JD-Xi editor

   This section contains the controls for the amp section of the JD-Xi editor.



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.analog.amp.AmpSection


Module Contents
---------------

.. py:class:: AmpSection(midi_helper: jdxi_editor.midi.io.helper.MidiIOHelper, address: jdxi_editor.midi.data.address.address.RolandSysExAddress, controls: dict[jdxi_editor.midi.data.parameter.AddressParameter, PySide6.QtWidgets.QWidget], create_parameter_slider: Callable, generate_waveform_icon: Callable, base64_to_pixmap: Callable)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Amp section of the JD-Xi editor


   .. py:attribute:: midi_helper


   .. py:attribute:: address


   .. py:attribute:: controls


   .. py:attribute:: _create_parameter_slider


   .. py:attribute:: generate_waveform_icon


   .. py:attribute:: base64_to_pixmap


   .. py:method:: init_ui()

      Initialize UI



