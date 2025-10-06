button.sequencer
================

.. py:module:: button.sequencer


Classes
-------

.. autoapisummary::

   button.sequencer.SequencerSquare


Module Contents
---------------

.. py:class:: SequencerSquare(slot_num, midi_helper: Optional[jdxi_editor.midi.io.helper.MidiIOHelper], parent=None)

   Bases: :py:obj:`PySide6.QtWidgets.QPushButton`


   Square button for sequencer/favorites with illuminated state


   .. py:attribute:: preset_loader
      :value: None



   .. py:attribute:: midi_helper


   .. py:attribute:: settings


   .. py:attribute:: slot_number


   .. py:attribute:: preset
      :value: None



   .. py:attribute:: last_preset
      :value: None



   .. py:attribute:: illuminated
      :value: False



   .. py:method:: _handle_toggle(checked)

      Handle button toggle



   .. py:method:: _handle_click(checked)

      Handle button toggle



   .. py:method:: paintEvent(event)

      Custom paint for illuminated appearance



   .. py:method:: save_preset_as_favourite(synth_type: str, preset_num: int, preset_name: str, channel: int)

      Save current preset to this favorite slot



   .. py:method:: clear_preset()

      Clear the saved preset



   .. py:method:: load_preset(preset_data)

      Load preset data into synth



