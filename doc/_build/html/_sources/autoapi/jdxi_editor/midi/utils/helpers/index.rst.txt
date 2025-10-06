jdxi_editor.midi.utils.helpers
==============================

.. py:module:: jdxi_editor.midi.utils.helpers


Functions
---------

.. autoapisummary::

   jdxi_editor.midi.utils.helpers.on_usb_recording_finished
   jdxi_editor.midi.utils.helpers.on_usb_recording_error
   jdxi_editor.midi.utils.helpers.start_recording


Module Contents
---------------

.. py:function:: on_usb_recording_finished(output_file: str)

   on_recording_finished

   :param output_file: str
   :return: None


.. py:function:: on_usb_recording_error(message: str)

   on_recording_error

   :param message: str
   :return: None


.. py:function:: start_recording(usb_recorder: jdxi_editor.midi.utils.usb_recorder.USBRecorder, file_duration_seconds: float, usb_file_output_name: str, recording_rate: int, selected_index: int) -> None

   start_recording

   :param usb_file_output_name: str
   :param file_duration_seconds: float
   :param usb_recorder: USBRecorder
   :param recording_rate: int
   :param selected_index: int
   :return: None

   Start the recording thread with the selected device index and recording rate.


