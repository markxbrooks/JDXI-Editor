piano.key
=========

.. py:module:: piano.key

.. autoapi-nested-parse::

   A custom Qt widget representing address piano key styled after the JD-Xi synthesizer keys.
   It defines address single class, PianoKey, which inherits from QPushButton and implements custom painting,
   mouse interaction, and simple animations to mimic the key press and release behavior of address physical piano key.

   Key Features:
   - Custom rendering with gradient fills to distinguish between black and white keys.
   - Visual feedback for key press events, including address color overlay and animated key movement.
   - Emission of custom signals (noteOn and noteOff) with the MIDI note number to integrate with audio systems.
   - Separate animations for key press and release, with different movement adjustments for black and white keys.

   Usage Example:
       from your_module import PianoKey
       key = PianoKey(note_num=60, is_black=False)
       key.noteOn.connect(handle_note_on)
       key.noteOff.connect(handle_note_off)

   Requires: PySide6.QtWidgets, PySide6.QtCore, PySide6.QtGui



Classes
-------

.. autoapisummary::

   piano.key.PianoKey


Module Contents
---------------

.. py:class:: PianoKey(note_num: int, is_black: bool = False, width: int = 22, height: int = 160, parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`PySide6.QtWidgets.QPushButton`


   Piano key styled like JD-Xi keys with animations and LED flicker


   .. py:attribute:: noteOn


   .. py:attribute:: noteOff


   .. py:attribute:: note_num


   .. py:attribute:: is_black
      :value: False



   .. py:attribute:: is_pressed
      :value: False



   .. py:attribute:: _geometry_initialized
      :value: False



   .. py:attribute:: press_animation


   .. py:attribute:: release_animation


   .. py:attribute:: stripe


   .. py:attribute:: led


   .. py:attribute:: led_effect


   .. py:attribute:: led_anim


   .. py:method:: showEvent(event: PySide6.QtGui.QShowEvent) -> None


   .. py:method:: mousePressEvent(event: PySide6.QtGui.QMouseEvent) -> None


   .. py:method:: mouseReleaseEvent(event: PySide6.QtGui.QMouseEvent) -> None


   .. py:method:: paintEvent(event: PySide6.QtGui.QPaintEvent) -> None


