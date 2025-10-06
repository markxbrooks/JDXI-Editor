jdxi_editor.ui.windows.midi.monitor
===================================

.. py:module:: jdxi_editor.ui.windows.midi.monitor

.. autoapi-nested-parse::

   message_debug module
   ====================

   MIDIMessageDebug is a Qt-based main window for logging and displaying MIDI messages.
   It provides a real-time log view where MIDI messages can be logged with timestamps,
   allowing for easy debugging of MIDI communication.

   .. attribute:: log_view

      A text edit widget used to display the MIDI message log.

      :type: :py:class:`QTextEdit`

   .. method:: log.message(message, direction="→")

      Logs a MIDI message with a timestamp.

   .. method:: Optionally, the direction (input or output) of the message can be specified.

      

   .. method:: clear_log()

      Clears the message log view.
      



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.windows.midi.monitor.MIDIMessageMonitor


Module Contents
---------------

.. py:class:: MIDIMessageMonitor(midi_helper: jdxi_editor.midi.io.helper.MidiIOHelper = None, parent: Optional[PySide6.QtWidgets.QWidget] = None)

   Bases: :py:obj:`PySide6.QtWidgets.QMainWindow`


   MIDIMessageMonitor


   .. py:attribute:: log_view


   .. py:attribute:: midi_helper
      :value: None



   .. py:method:: process_incoming_message(message: str) -> None

      process_incoming_message

      :param message: str
      :return: None



   .. py:method:: process_outgoing_message(message: str) -> None

      process_outgoing_message

      :param message: str
      :return: None



   .. py:method:: log_message(message: str, direction='→')

      Log address MIDI message with timestamp and hex formatting if possible

      :param message: str
      :param direction: str
      :return: None



   .. py:method:: clear_log()

      Clear the log view



