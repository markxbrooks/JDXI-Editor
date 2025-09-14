adsr.adsr
=========

.. py:module:: adsr.adsr

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

   adsr.adsr.ADSR


Module Contents
---------------

.. py:class:: ADSR(attack_param: jdxi_editor.midi.data.parameter.synth.AddressParameter, decay_param: jdxi_editor.midi.data.parameter.synth.AddressParameter, sustain_param: jdxi_editor.midi.data.parameter.synth.AddressParameter, release_param: jdxi_editor.midi.data.parameter.synth.AddressParameter, initial_param: Optional[jdxi_editor.midi.data.parameter.synth.AddressParameter] = None, peak_param: Optional[jdxi_editor.midi.data.parameter.synth.AddressParameter] = None, create_parameter_slider: Callable = None, midi_helper: Optional[jdxi_editor.midi.io.helper.MidiIOHelper] = None, address: Optional[jdxi_editor.midi.data.address.address.RolandSysExAddress] = None, controls: Dict[jdxi_editor.midi.data.parameter.synth.AddressParameter, PySide6.QtWidgets.QWidget] = None, parent: Optional[PySide6.QtWidgets.QWidget] = None)

   Bases: :py:obj:`jdxi_editor.ui.widgets.envelope.base.EnvelopeWidgetBase`


   ADSR Widget for Roland JD-Xi


   .. py:attribute:: envelope_changed


   .. py:attribute:: sysex_composer

      Initialize the ADSR widget

      :param attack_param: AddressParameter
      :param decay_param: AddressParameter
      :param sustain_param: AddressParameter
      :param release_param: AddressParameter
      :param initial_param: Optional[AddressParameter]
      :param peak_param: Optional[AddressParameter]
      :param midi_helper: Optional[MidiIOHelper]
      :param address: Optional[RolandSysExAddress]
      :param parent: Optional[QWidget]


   .. py:attribute:: address
      :value: None



   .. py:attribute:: midi_helper
      :value: None



   .. py:attribute:: _create_parameter_slider
      :value: None



   .. py:attribute:: envelope


   .. py:attribute:: attack_control


   .. py:attribute:: decay_control


   .. py:attribute:: sustain_control


   .. py:attribute:: release_control


   .. py:attribute:: _control_widgets


   .. py:attribute:: attack_parameter


   .. py:attribute:: decay_parameter


   .. py:attribute:: sustain_parameter


   .. py:attribute:: release_parameter


   .. py:attribute:: _control_parameters


   .. py:attribute:: layout


   .. py:attribute:: envelope_spinbox_map


   .. py:attribute:: plot


   .. py:method:: on_control_changed(change: dict)


   .. py:method:: update_envelope_from_spinboxes()

      Update envelope values from spin boxes



   .. py:method:: update_spinboxes_from_envelope()

      Update spinboxes from envelope values



