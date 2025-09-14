button
======

.. py:module:: button


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/button/channel/index
   /autoapi/button/favorite/index
   /autoapi/button/sequencer/index
   /autoapi/button/waveform/index


Classes
-------

.. autoapisummary::

   button.ChannelButton
   button.SequencerSquare


Package Contents
----------------

.. py:class:: ChannelButton(parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`PySide6.QtWidgets.QPushButton`


   Channel indicator button with synth-specific styling


   .. py:attribute:: CHANNEL_STYLES


   .. py:attribute:: current_channel
      :value: 0



   .. py:method:: set_channel(channel: int) -> None

      Set channel and update appearance

      :param channel: int



   .. py:method:: _update_style() -> None

      Update button appearance based on channel

      :return: None



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



