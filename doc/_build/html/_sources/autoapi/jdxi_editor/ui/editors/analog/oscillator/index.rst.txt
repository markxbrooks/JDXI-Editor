jdxi_editor.ui.editors.analog.oscillator
========================================

.. py:module:: jdxi_editor.ui.editors.analog.oscillator

.. autoapi-nested-parse::

   Analog Oscillator Section



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.analog.oscillator.AnalogOscillatorSection


Module Contents
---------------

.. py:class:: AnalogOscillatorSection(create_parameter_slider: Callable, create_parameter_switch: Callable, waveform_selected_callback: Callable, wave_buttons: dict, midi_helper: jdxi_editor.midi.io.helper.MidiIOHelper, controls: dict[jdxi_editor.midi.data.parameter.AddressParameter, PySide6.QtWidgets.QWidget], address: jdxi_editor.midi.data.address.address.RolandSysExAddress)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Analog Oscillator Section


   .. py:attribute:: pitch_env_widget
      :value: None



   .. py:attribute:: pwm_widget
      :value: None



   .. py:attribute:: _create_parameter_slider


   .. py:attribute:: _create_parameter_switch


   .. py:attribute:: _on_waveform_selected


   .. py:attribute:: wave_buttons


   .. py:attribute:: midi_helper


   .. py:attribute:: address


   .. py:attribute:: controls


   .. py:method:: init_ui() -> None

      Initialize the UI
      :return: None



   .. py:method:: create_waveform_buttons() -> PySide6.QtWidgets.QHBoxLayout

      Create the waveform buttons

      :return: QHBoxLayout



   .. py:method:: create_tuning_group() -> PySide6.QtWidgets.QGroupBox

      Create the tuning group

      :return: QGroupBox



   .. py:method:: create_pw_group() -> PySide6.QtWidgets.QGroupBox

      Create the pulse width group

      :return: QGroupBox



   .. py:method:: create_pitch_env_group() -> PySide6.QtWidgets.QGroupBox

      Create the pitch envelope group

      :return: QGroupBox



   .. py:method:: _update_pw_controls_state(waveform: jdxi_editor.midi.data.analog.oscillator.AnalogOscWave)

      Update pulse width controls enabled state based on waveform

      :param waveform: AnalogOscWave value
      :return: None



