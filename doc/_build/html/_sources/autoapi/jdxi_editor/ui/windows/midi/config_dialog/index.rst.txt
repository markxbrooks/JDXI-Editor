jdxi_editor.ui.windows.midi.config_dialog
=========================================

.. py:module:: jdxi_editor.ui.windows.midi.config_dialog

.. autoapi-nested-parse::

   config_dialog module
   ====================

   MIDIConfigDialog is a dialog class that allows users to configure MIDI input and output ports.

   It provides the following functionality:
   - Display available MIDI input and output ports in combo boxes.
   - Allow users to select and change MIDI input and output ports.
   - Refresh the list of available MIDI ports.
   - Retrieve the selected MIDI port settings.

   .. attribute:: input_ports

      List of available MIDI input ports.

      :type: :py:class:`list`

   .. attribute:: output_ports

      List of available MIDI output ports.

      :type: :py:class:`list`

   .. attribute:: current_in

      Currently selected MIDI input port (optional).

      :type: :py:class:`str`

   .. attribute:: current_out

      Currently selected MIDI output port (optional).

      :type: :py:class:`str`

   .. attribute:: midi_helper

      Instance of the MIDIHelper class to interact with MIDI devices.

      :type: :py:class:`MidiIOHelper`

   .. method:: refresh_ports()

      Refresh the list of available MIDI ports.

   .. method:: get_input_port()

      Returns the currently selected MIDI input port.

   .. method:: get_output_port()

      Returns the currently selected MIDI output port.

   .. method:: get_settings()

      Returns a dictionary containing the selected MIDI input and output ports.
      



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.windows.midi.config_dialog.MIDIConfigDialog


Module Contents
---------------

.. py:class:: MIDIConfigDialog(midi_helper=MidiIOHelper, parent=None)

   Bases: :py:obj:`PySide6.QtWidgets.QDialog`


   .. py:attribute:: midi_helper


   .. py:attribute:: input_ports


   .. py:attribute:: output_ports


   .. py:attribute:: current_in


   .. py:attribute:: current_out


   .. py:method:: _create_ui()

      Create the dialog UI



   .. py:method:: refresh_ports()

      Refresh the list of MIDI ports



   .. py:method:: accept()


   .. py:method:: get_input_port() -> str

      Get selected input port name

      :returns: Selected input port name or empty string if none selected



   .. py:method:: get_output_port() -> str

      Get selected output port name

      :returns: Selected output port name or empty string if none selected



   .. py:method:: get_settings() -> dict

      Get all selected settings

      :returns: Dictionary containing input_port and output_port selections



