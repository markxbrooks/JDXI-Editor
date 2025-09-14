midi.slider.lfo.pitch_depth
===========================

.. py:module:: midi.slider.lfo.pitch_depth

.. autoapi-nested-parse::

   filter slider to modify nrpn parameters

   CC#99 – NRPN MSB

   CC#98 – NRPN LSB

   CC#6 – Data Entry MSB (value: 0–127)

   (Optional) CC#38 – Data Entry LSB (if 14-bit needed, but not in your case)

   CC#101 & 100 – Reset to NULL (optional, to avoid data confusion)



Classes
-------

.. autoapisummary::

   midi.slider.lfo.pitch_depth.LFOPitchSlider


Module Contents
---------------

.. py:class:: LFOPitchSlider(midi_helper, label: str = 'LFO Pitch Depth')

   Bases: :py:obj:`jdxi_editor.ui.widgets.midi.slider.nrpn.NRPNSlider`


   A slider for controlling LFO Pitch Depth for JD-Xi partials via NRPN.


