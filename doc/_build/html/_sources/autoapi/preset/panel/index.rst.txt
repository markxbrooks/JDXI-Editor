preset.panel
============

.. py:module:: preset.panel

.. autoapi-nested-parse::

   Panel for loading/saving presets



Classes
-------

.. autoapisummary::

   preset.panel.PresetPanel


Module Contents
---------------

.. py:class:: PresetPanel(midi_helper: jdxi_editor.midi.io.helper.MidiIOHelper, parent=None)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Panel for loading/saving presets


   .. py:attribute:: load_clicked


   .. py:attribute:: save_clicked


   .. py:attribute:: preset_combo


   .. py:attribute:: analog_editor


   .. py:attribute:: digital_1_editor


   .. py:attribute:: digital_2_editor


   .. py:attribute:: drums_editor


   .. py:method:: _on_load()

      Handle load button click



   .. py:method:: _on_save()

      Handle save button click



