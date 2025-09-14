jdxi_editor.ui.editors.digital
==============================

.. py:module:: jdxi_editor.ui.editors.digital


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/jdxi_editor/ui/editors/digital/common/index
   /autoapi/jdxi_editor/ui/editors/digital/editor/index
   /autoapi/jdxi_editor/ui/editors/digital/partial/index
   /autoapi/jdxi_editor/ui/editors/digital/tone_modify/index
   /autoapi/jdxi_editor/ui/editors/digital/utils/index


Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.digital.DigitalCommonSection
   jdxi_editor.ui.editors.digital.DigitalToneModifySection
   jdxi_editor.ui.editors.digital.DigitalPartialEditor


Package Contents
----------------

.. py:class:: DigitalCommonSection(create_parameter_slider: Callable, create_parameter_switch: Callable, create_parameter_combo_box: Callable, controls: dict)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   .. py:attribute:: _create_parameter_slider


   .. py:attribute:: _create_parameter_switch


   .. py:attribute:: _create_parameter_combo_box


   .. py:attribute:: controls


   .. py:method:: init_ui()


.. py:class:: DigitalToneModifySection(create_parameter_slider: Callable, create_parameter_combo_box: Callable, create_parameter_switch: Callable, controls: dict)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   .. py:attribute:: _create_parameter_slider


   .. py:attribute:: _create_parameter_combo_box


   .. py:attribute:: _create_parameter_switch


   .. py:attribute:: controls


   .. py:method:: init_ui()

      Initialize the UI for the DigitalToneModifySection



.. py:class:: DigitalPartialEditor(midi_helper: Optional[jdxi_editor.midi.io.helper.MidiIOHelper] = None, synth_number: int = 1, partial_number: int = 1, preset_type: jdxi_editor.jdxi.synth.type.JDXiSynth = None, parent: Optional[PySide6.QtWidgets.QWidget] = None)

   Bases: :py:obj:`jdxi_editor.ui.editors.synth.partial.PartialEditor`


   Editor for address single partial


   .. py:attribute:: filter_mode_switch
      :value: None


      Initialize the DigitalPartialEditor

      :param midi_helper: MidiIOHelper
      :param synth_number: int
      :param partial_number: int
      :param preset_type: JDXiSynth
      :param parent: QWidget


   .. py:attribute:: partial_address_default


   .. py:attribute:: partial_address_map


   .. py:attribute:: bipolar_parameters


   .. py:attribute:: midi_helper
      :value: None



   .. py:attribute:: partial_number
      :value: 1



   .. py:attribute:: preset_type
      :value: None



   .. py:attribute:: controls
      :type:  Dict[Union[jdxi_editor.midi.data.parameter.digital.partial.AddressParameterDigitalPartial, jdxi_editor.midi.data.parameter.digital.common.AddressParameterDigitalCommon], PySide6.QtWidgets.QWidget]


   .. py:attribute:: tab_widget


   .. py:attribute:: oscillator_tab


   .. py:attribute:: filter_tab


   .. py:attribute:: amp_tab


   .. py:attribute:: lfo_tab


   .. py:attribute:: mod_lfo_tab


   .. py:attribute:: updating_from_spinbox
      :value: False



   .. py:method:: __str__()


   .. py:method:: __repr__()


   .. py:method:: update_filter_controls_state(mode: int)

      Update filter controls enabled state based on mode

      :param mode: int



   .. py:method:: _on_waveform_selected(waveform: jdxi_editor.midi.data.digital.oscillator.DigitalOscWave)

      Handle waveform button clicks

      :param waveform: DigitalOscWave



