pitch.envelope
==============

.. py:module:: pitch.envelope

.. autoapi-nested-parse::

   ADSR Widget for Roland JD-Xi

   This widget provides address visual interface for editing ADSR (Attack, Decay, Sustain, Release)
   envelope parameters. It includes:
   - Interactive sliders for each ADSR parameter
   - Visual envelope plot
   - Real-time parameter updates
   - MIDI parameter integration via SynthParameter objects

   The widget supports both analog and digital synth parameters and provides visual feedback
   through an animated envelope curve.



Classes
-------

.. autoapisummary::

   pitch.envelope.PitchEnvelopeWidget


Module Contents
---------------

.. py:class:: PitchEnvelopeWidget(attack_param: jdxi_editor.midi.data.parameter.synth.AddressParameter, decay_param: jdxi_editor.midi.data.parameter.synth.AddressParameter, depth_param: jdxi_editor.midi.data.parameter.synth.AddressParameter, midi_helper: Optional[jdxi_editor.midi.io.helper.MidiIOHelper] = None, create_parameter_slider: Callable = None, controls: dict[jdxi_editor.midi.data.parameter.synth.AddressParameter, PySide6.QtWidgets.QWidget] = None, address: Optional[jdxi_editor.midi.data.address.address.RolandSysExAddress] = None, parent: Optional[PySide6.QtWidgets.QWidget] = None)

   Bases: :py:obj:`jdxi_editor.ui.widgets.envelope.base.EnvelopeWidgetBase`


   Pitch Envelope Class


   .. py:attribute:: envelope_changed


   .. py:attribute:: address
      :value: None



   .. py:attribute:: midi_helper
      :value: None



   .. py:attribute:: _create_parameter_slider
      :value: None



   .. py:attribute:: envelope


   .. py:attribute:: attack_control


   .. py:attribute:: decay_control


   .. py:attribute:: depth_control


   .. py:attribute:: _control_widgets


   .. py:attribute:: envelope_spinbox_map


   .. py:attribute:: plot


   .. py:attribute:: layout


   .. py:method:: on_control_changed(change: dict) -> None

      Control Change callback

      :param change: dict envelope
      :return: None
      :emits: dict pitch envelope parameters



   .. py:method:: update_envelope_from_spinboxes()

      Update envelope values from spinboxes
      :emits: dict pitch envelope parameters



   .. py:method:: update_spinboxes_from_envelope()

      Update spinboxes from envelope values
      :emits: dict pitch envelope parameters



   .. py:method:: update_envelope_from_slider(slider: PySide6.QtWidgets.QSlider) -> None

      Update envelope with value from a single slider



   .. py:method:: update_envelope_from_controls() -> None

      Update envelope values from slider controls



   .. py:method:: update_controls_from_envelope() -> None

      Update slider controls from envelope values.



