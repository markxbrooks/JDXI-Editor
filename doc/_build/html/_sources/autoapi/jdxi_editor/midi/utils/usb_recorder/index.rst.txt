jdxi_editor.midi.utils.usb_recorder
===================================

.. py:module:: jdxi_editor.midi.utils.usb_recorder


Attributes
----------

.. autoapisummary::

   jdxi_editor.midi.utils.usb_recorder.recorder


Classes
-------

.. autoapisummary::

   jdxi_editor.midi.utils.usb_recorder.USBRecorder


Module Contents
---------------

.. py:class:: USBRecorder(input_device_index: int = None, channels: int = 1, rate: int = 44100, frames_per_buffer: int = 1024)

   A convenient class for recording audio from a USB input device.


   .. py:attribute:: p


   .. py:attribute:: input_device_index
      :value: None



   .. py:attribute:: channels
      :value: 1



   .. py:attribute:: rate
      :value: 44100



   .. py:attribute:: frames_per_buffer
      :value: 1024



   .. py:attribute:: file_save_recording
      :value: True



   .. py:attribute:: usb_port_input_device_index
      :value: None



   .. py:attribute:: usb_recording_rates


   .. py:method:: list_devices()

      Prints a list of available audio input devices.



   .. py:method:: record(duration, output_file, rate='16bit')

      Records audio for the specified duration and saves to a .wav file.



   .. py:method:: close()

      Closes the PyAudio instance.



   .. py:method:: stop_recording()

      stop_recording

      :return: None



.. py:data:: recorder

