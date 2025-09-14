midi.track_viewer
=================

.. py:module:: midi.track_viewer

.. autoapi-nested-parse::

   Midi Track Viewer



Classes
-------

.. autoapisummary::

   midi.track_viewer.MidiTrackViewer


Module Contents
---------------

.. py:class:: MidiTrackViewer(parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   MidiTrackViewer


   .. py:attribute:: midi_file
      :value: None



   .. py:attribute:: event_index
      :value: None



   .. py:attribute:: ruler


   .. py:attribute:: midi_track_widgets


   .. py:attribute:: muted_tracks
      :type:  set[int]


   .. py:attribute:: muted_channels
      :type:  set[int]


   .. py:attribute:: scroll_content


   .. py:attribute:: mute_buttons


   .. py:attribute:: track_zoom_slider


   .. py:method:: clear()

      Clear the MIDI track view and reset state.



   .. py:method:: _clear_layout(layout: PySide6.QtWidgets.QLayout)

      _clear_layout

      :param layout:
      :return:
      Recursively clear a layout and its children.



   .. py:method:: clear_old()

      Clear the MIDI track view and reset state.



   .. py:method:: update_track_zoom(width: int)

      update_track_zoom

      :param width: int
      :return: None



   .. py:method:: toggle_channel_mute(channel: int, is_muted: bool) -> None

      Toggle mute state for a specific MIDI channel.

      :param channel: int MIDI channel (1-16)
      :param is_muted: bool is the channel muted?
      :return: None



   .. py:method:: update_muted_channels(muted_channels: set[int]) -> None

      Called when the global mute state is updated.



   .. py:method:: toggle_track_mute(track: int, is_muted: bool) -> None

      Toggle mute state for a specific MIDI track.

      :param track: int MIDI channel (1-16)
      :param is_muted: bool is the channel muted?
      :return: None



   .. py:method:: update_muted_tracks(muted_tracks: set[int]) -> None

      Called when the global mute state is updated.



   .. py:method:: mute_track(track_index: int) -> None

      Mute a specific track

      :param track_index: int
      :return: None



   .. py:method:: delete_track(track_index: int) -> None

      Ask user to confirm and delete a specific MIDI track and its widget.

      :param track_index: int
      :return: None



   .. py:method:: change_track_name(track_index: int, new_name: str) -> None

      Change the name of a specific MIDI track.

      :param track_index: int
      :param new_name: str
      :return: None



   .. py:method:: set_track_name(track, new_name)


   .. py:method:: change_track_channel(track_index: int, new_channel: int) -> None

      Change the MIDI channel of a specific track.

      :param track_index: int
      :param new_channel: int
      :return: None



   .. py:method:: make_apply_slot(track_index: int, spin_box: jdxi_editor.ui.widgets.midi.spin_box.spin_box.MidiSpinBox) -> callable

      Create a slot for applying changes to the track channel.

      :param track_index: int Track index to modify
      :param spin_box: MidiSpinBox Spin box for selecting the channel
      :return: callable function to apply changes



   .. py:method:: make_apply_name(track_name: str, text_edit: PySide6.QtWidgets.QLineEdit) -> callable

      Create a slot for applying changes to the track channel.

      :param track_name: str Track name to modify
      :param text_edit: QLineEdit for selecting the name
      :return: callable function to apply changes



   .. py:method:: set_midi_file(midi_file: mido.MidiFile) -> None

      Set the MIDI file for the widget and create channel controls.

      :param midi_file:
      :return: None



   .. py:method:: get_track_controls_width() -> int

      Returns the estimated total width of all controls to the left of the MidiTrackWidget.



   .. py:method:: clear_layout(layout: PySide6.QtWidgets.QLayout) -> None


   .. py:method:: refresh_track_list()

      refresh_track_list

      :return:



   .. py:method:: get_muted_channels()


   .. py:method:: get_muted_tracks()


