midi.slider.lfo
===============

.. py:module:: midi.slider.lfo


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/midi/slider/lfo/amp_depth/index
   /autoapi/midi/slider/lfo/filter_depth/index
   /autoapi/midi/slider/lfo/pitch_depth/index
   /autoapi/midi/slider/lfo/rate/index
   /autoapi/midi/slider/lfo/shape/index


Classes
-------

.. autoapisummary::

   midi.slider.lfo.LFOAmpDepthSlider
   midi.slider.lfo.LFOFilterDepthSlider
   midi.slider.lfo.LFOPitchSlider
   midi.slider.lfo.LFORateSlider


Package Contents
----------------

.. py:class:: LFOAmpDepthSlider(midi_helper, label: str = 'LFO Pitch Depth')

   Bases: :py:obj:`jdxi_editor.ui.widgets.midi.slider.nrpn.NRPNSlider`


   A slider for controlling LFO Pitch Depth for JD-Xi partials via NRPN.


.. py:class:: LFOFilterDepthSlider(midi_helper, label: str = 'LFO Pitch Depth', is_bipolar=True)

   Bases: :py:obj:`jdxi_editor.ui.widgets.midi.slider.nrpn.NRPNSlider`


   A slider for controlling LFO Pitch Depth for JD-Xi partials via NRPN.


.. py:class:: LFOPitchSlider(midi_helper, label: str = 'LFO Pitch Depth')

   Bases: :py:obj:`jdxi_editor.ui.widgets.midi.slider.nrpn.NRPNSlider`


   A slider for controlling LFO Pitch Depth for JD-Xi partials via NRPN.


.. py:class:: LFORateSlider(midi_helper, label: str = 'Reson.')

   Bases: :py:obj:`jdxi_editor.ui.widgets.midi.slider.nrpn.NRPNSlider`


   A class to represent a amp slider for JD-Xi using NRPN.


