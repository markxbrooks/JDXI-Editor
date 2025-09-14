midi.slider.control_change
==========================

.. py:module:: midi.slider.control_change

.. autoapi-nested-parse::

   Control Change Slider

   sends CC, (N)RPN messages to the synth

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

   midi.slider.control_change.ControlChangeSlider


Module Contents
---------------

.. py:class:: ControlChangeSlider(midi_helper, label: str, nrpn_map: dict, partial: int = 1, min_value: int = 0, max_value: int = 127, vertical: bool = True, channels: list = [0, 1, 2], is_bipolar=False)

   Bases: :py:obj:`jdxi_editor.ui.widgets.slider.Slider`


   A base class for sliders with a common on_valueChanged method to send Control Change (CC) messages.


   .. py:attribute:: channels
      :value: [0, 1, 2]



   .. py:attribute:: label


   .. py:attribute:: current_value
      :value: 0



   .. py:attribute:: vertical
      :value: True



   .. py:attribute:: nrpn_map


   .. py:method:: update_style(value: int) -> None

      Update the style of the slider.

      :param value: int



   .. py:method:: on_valueChanged(value: int)

      Set the current value of the slider and send Control Change (CC) messages.

      :param value: int



