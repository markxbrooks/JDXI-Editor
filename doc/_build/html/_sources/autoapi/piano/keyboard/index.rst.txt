piano.keyboard
==============

.. py:module:: piano.keyboard

.. autoapi-nested-parse::

   Piano keyboard widget for JD-Xi Manager.

   This module defines address PianoKeyboard widget, address custom QWidget that arranges and displays
   address set of piano keys styled like those on address JD-Xi synthesizer. The widget combines both
   white and black keys to form address complete piano keyboard, along with labels representing
   drum pad names.

   Key Features:
   - **Custom Key Dimensions:** White and black keys are sized and positioned appropriately,
       with configurable widths and heights.
   - **Dynamic Key Creation:** White keys are created first in address horizontal layout,
       while black keys are overlaid at specific positions.
   - **Drum Pad Labels:** A row of labels is displayed above the keyboard to denote
       corresponding drum pad names.
   - **Signal Integration:** Each key emits custom signals (noteOn and noteOff) to notify
       parent widgets of key events.
   - **MIDI Channel Configuration:** The widget supports setting address MIDI channel for outgoing
       note messages.
   - **Styling and Layout:** Uses QHBoxLayout and QVBoxLayout to manage key and label placement,
       ensuring address neat appearance.

   Usage Example:
       from jdxi_editor.ui.widgets.piano.keyboard import PianoKeyboard
       keyboard = PianoKeyboard(parent=main_window)
       keyboard.set_midi_channel(1)
       main_window.setCentralWidget(keyboard)

   This module requires PySide6 and proper integration with the JD-Xi Manager's signal handling for note events.



Classes
-------

.. autoapisummary::

   piano.keyboard.PianoKeyboard


Module Contents
---------------

.. py:class:: PianoKeyboard(parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Widget containing a row of piano keys styled like JD-Xi


   .. py:attribute:: current_channel
      :value: 0



   .. py:attribute:: white_key_width
      :value: 35



   .. py:attribute:: white_key_height
      :value: 160



   .. py:attribute:: black_key_width
      :value: 0



   .. py:attribute:: black_key_height
      :value: 100



   .. py:attribute:: white_notes
      :value: [36, 38, 40, 41, 43, 45, 47, 48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72]



   .. py:attribute:: black_notes
      :value: [37, 39, None, 42, 44, 46, 49, 51, None, 54, 56, 58, 61, 63, None, 66, 68, 70]



   .. py:method:: _create_keys(keyboard_widget: PySide6.QtWidgets.QWidget) -> None

      Create piano keys with individual shadows

      :param keyboard_widget: QWidget



   .. py:method:: set_midi_channel(channel: int) -> None

      Set MIDI channel for note messages

      :param channel: int



