jdxi_editor.ui.editors.digital.partial.amp
==========================================

.. py:module:: jdxi_editor.ui.editors.digital.partial.amp

.. autoapi-nested-parse::

   AMP section for the digital partial editor.



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.digital.partial.amp.DigitalAmpSection


Module Contents
---------------

.. py:class:: DigitalAmpSection(create_parameter_slider: Callable, partial_number: int, midi_helper: jdxi_editor.midi.io.helper.MidiIOHelper, controls: dict[jdxi_editor.midi.data.parameter.AddressParameter, PySide6.QtWidgets.QWidget], address: jdxi_editor.midi.data.address.address.RolandSysExAddress)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Digital Amp Section for the JDXI Editor


   .. py:attribute:: partial_number


   .. py:attribute:: midi_helper


   .. py:attribute:: address


   .. py:attribute:: controls


   .. py:attribute:: _create_parameter_slider


   .. py:method:: setup_ui()

      Setup the amplifier section UI.



