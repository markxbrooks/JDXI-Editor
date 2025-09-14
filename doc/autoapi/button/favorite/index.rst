button.favorite
===============

.. py:module:: button.favorite

.. autoapi-nested-parse::

   Favorite Button



Classes
-------

.. autoapisummary::

   button.favorite.FavoriteButton


Module Contents
---------------

.. py:class:: FavoriteButton(slot_num: int, midi_helper: jdxi_editor.midi.io.helper.MidiIOHelper, parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`PySide6.QtWidgets.QPushButton`


   Favorite preset button with save/recall functionality


   .. py:attribute:: preset_selected


   .. py:attribute:: last_preset
      :value: None



   .. py:attribute:: preset_helper
      :value: None



   .. py:attribute:: midi_helper


   .. py:attribute:: slot_num


   .. py:attribute:: preset
      :value: None



   .. py:attribute:: settings


   .. py:method:: save_preset_as_favourite(synth_type: str, preset_num: int, preset_name: str, channel: int) -> None

      Save current preset to this favorite slot

      :param synth_type: str
      :param preset_num: int
      :param preset_name: str
      :param channel: int



   .. py:method:: load_preset_from_favourites()

      Load saved preset



   .. py:method:: load_preset(preset_data: jdxi_editor.jdxi.preset.data.JDXiPresetData)

      Load preset data into synth



   .. py:method:: _save_to_settings()

      Save preset data to settings



   .. py:method:: _load_from_settings()

      Load preset data from settings



   .. py:method:: clear_preset()

      Clear the saved preset



   .. py:method:: _update_style()

      Update button appearance



