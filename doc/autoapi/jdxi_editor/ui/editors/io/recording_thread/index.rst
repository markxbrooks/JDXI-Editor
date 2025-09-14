jdxi_editor.ui.editors.io.recording_thread
==========================================

.. py:module:: jdxi_editor.ui.editors.io.recording_thread


Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.io.recording_thread.WavRecordingThread


Module Contents
---------------

.. py:class:: WavRecordingThread(recorder: jdxi_editor.midi.utils.usb_recorder.USBRecorder, duration: float = None, output_file: str = None, recording_rate=pyaudio.paInt16, parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`PySide6.QtCore.QThread`


   WavRecordingThread


   .. py:attribute:: recording_finished


   .. py:attribute:: recording_error


   .. py:attribute:: recorder


   .. py:attribute:: recording_rate


   .. py:attribute:: duration
      :value: None



   .. py:attribute:: output_file
      :value: None



   .. py:attribute:: running
      :value: False



   .. py:method:: run()


   .. py:method:: record()

      Records audio for the specified duration or until stopped gracefully.



   .. py:method:: record_old()

      Records audio for the specified duration and saves to a .wav file.



   .. py:method:: stop_recording()

      stop_recording

      :return: None



