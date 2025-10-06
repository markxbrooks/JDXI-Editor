jdxi_editor.ui.editors.synth.partial
====================================

.. py:module:: jdxi_editor.ui.editors.synth.partial

.. autoapi-nested-parse::

   Module for the PartialEditor widget, which provides a UI for editing individual partial parameters of a synthesizer.

   This module defines the `PartialEditor` class, which extends `QWidget` to offer an interface for modifying
   synth parameters through sliders, combo boxes, and spin boxes. It integrates with a MIDI helper to send parameter
   changes to the synthesizer in real-time.

   Classes:
       PartialEditor: A QWidget-based editor for modifying individual partial parameters.

   Dependencies:
       - PySide6.QtWidgets (QWidget)
       - logging
       - typing (Dict)
       - jdxi_manager.midi.data.parameter.synth (SynthParameter)
       - jdxi_manager.midi.data.constants (PART_1)
       - jdxi_manager.ui.widgets.slider (Slider)
       - jdxi_manager.ui.widgets.combo_box.combo_box (ComboBox)
       - jdxi_manager.ui.widgets.spin_box.spin_box (SpinBox)



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.synth.partial.PartialEditor


Module Contents
---------------

.. py:class:: PartialEditor(midi_helper=None, partial_number=1, parent=None)

   Bases: :py:obj:`jdxi_editor.ui.editors.synth.base.SynthBase`


   Editor for address single partial


   .. py:attribute:: synth_data
      :value: None



   .. py:attribute:: partial_address_default
      :value: None



   .. py:attribute:: partial_address_map


   .. py:attribute:: bipolar_parameters
      :value: []



   .. py:attribute:: midi_helper
      :value: None



   .. py:attribute:: partial_number
      :value: 1



   .. py:attribute:: partial_name
      :value: None



   .. py:attribute:: preset_helper
      :value: None



   .. py:attribute:: controls
      :type:  Dict[jdxi_editor.midi.data.parameter.synth.AddressParameter, PySide6.QtWidgets.QWidget]


   .. py:method:: __str__()


   .. py:method:: __repr__()


