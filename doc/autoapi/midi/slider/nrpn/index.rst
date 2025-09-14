midi.slider.nrpn
================

.. py:module:: midi.slider.nrpn

.. autoapi-nested-parse::

   NRPN Slider
   sends NRPN, (N)RPN messages to the synth

   def send_nrpn(self, channel, msb, lsb, value):
       self.send_control_change(99, msb, channel)  # NRPN MSB
       self.send_control_change(98, lsb, channel)  # NRPN LSB
       self.send_control_change(6, value, channel)  # Data Entry MSB
       # Optional: Reset NRPN selection
       self.send_control_change(99, 127, channel)
       self.send_control_change(98, 127, channel)



Classes
-------

.. autoapisummary::

   midi.slider.nrpn.NRPNSlider


Module Contents
---------------

.. py:class:: NRPNSlider(midi_helper, label: str, nrpn_map: dict, partial: int = 1, nrpn_msb: int = 0, min_value: int = 0, max_value: int = 127, vertical: bool = True, param_type: str = 'nrpn', is_bipolar: bool = False)

   Bases: :py:obj:`jdxi_editor.ui.widgets.slider.Slider`


   A base class for sliders that send NRPN messages to a specified partial.


   .. py:attribute:: label


   .. py:attribute:: midi_helper


   .. py:attribute:: partial
      :value: 1



   .. py:attribute:: nrpn_map


   .. py:attribute:: nrpn_msb
      :value: 0



   .. py:attribute:: min_value
      :value: 0



   .. py:attribute:: max_value
      :value: 127



   .. py:attribute:: current_value
      :value: 0



   .. py:attribute:: vertical
      :value: True



   .. py:attribute:: param_type
      :value: 'nrpn'



   .. py:attribute:: midi_requests


   .. py:method:: update_style(value: int) -> None

      Update the style of the slider.

      :param value: int



   .. py:method:: data_request() -> None

      Request the current value of the NRPN parameter from the device.



   .. py:method:: on_valueChanged(value: int)

      Set the current value of the slider and send NRPN or RPN messages

      :param value: int



