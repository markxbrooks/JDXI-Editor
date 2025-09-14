jdxi_editor.ui.editors.digital.partial.oscillator
=================================================

.. py:module:: jdxi_editor.ui.editors.digital.partial.oscillator

.. autoapi-nested-parse::

   Digital Oscillator Section for the JDXI Editor



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.digital.partial.oscillator.DigitalOscillatorSection


Module Contents
---------------

.. py:class:: DigitalOscillatorSection(create_parameter_slider: Callable, create_parameter_switch: Callable, create_parameter_combo_box: Callable, send_midi_parameter: Callable, partial_number: int, midi_helper: jdxi_editor.midi.io.helper.MidiIOHelper, controls: dict[jdxi_editor.midi.data.parameter.AddressParameter, PySide6.QtWidgets.QWidget], address: jdxi_editor.midi.data.address.address.RolandSysExAddress)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Digital Oscillator Section for the JDXI Editor


   .. py:attribute:: pwm_widget
      :value: None



   .. py:attribute:: partial_number


   .. py:attribute:: midi_helper


   .. py:attribute:: controls


   .. py:attribute:: _create_parameter_slider


   .. py:attribute:: _create_parameter_switch


   .. py:attribute:: _create_parameter_combo_box


   .. py:attribute:: send_midi_parameter


   .. py:attribute:: address


   .. py:method:: setup_ui()

      Setup the oscillator section UI.



   .. py:method:: _on_waveform_selected(waveform: jdxi_editor.midi.data.digital.oscillator.DigitalOscWave)

      Handle waveform button clicks



   .. py:method:: _update_waveform_controls_enabled_states(waveform: jdxi_editor.midi.data.digital.oscillator.DigitalOscWave)

      _update_waveform_controls_states

      :param waveform: DigitalOscWave
      :return: None

      Update control visibility and enabled state based on the selected waveform.



   .. py:method:: update_waves()

      Update PCM waves based on selected category



   .. py:method:: _update_pw_controls_enabled_state(waveform: jdxi_editor.midi.data.digital.oscillator.DigitalOscWave)

      Update pulse width controls enabled state based on waveform



   .. py:method:: _update_pcm_controls_enabled_state(waveform: jdxi_editor.midi.data.digital.oscillator.DigitalOscWave)

      Update PCM wave controls visibility based on waveform



   .. py:method:: _update_supersaw_controls_enabled_state(waveform: jdxi_editor.midi.data.digital.oscillator.DigitalOscWave)

      Update supersaw controls visibility based on waveform



