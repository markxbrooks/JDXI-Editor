display.digital
===============

.. py:module:: display.digital

.. autoapi-nested-parse::

   digital_display.py

   This module provides the DigitalDisplay class, a custom PySide6 QWidget designed
   to simulate an LCD-style digital display for MIDI controllers, synthesizers,
   or other music-related applications. The display shows preset and program
   information along with an octave indicator.

   Features:
   - Displays a program name, program number, preset name, and preset number.
   - Shows the current octave with a digital-style font.
   - Customizable font family for the digital display.
   - Resizable and styled for a retro LCD appearance.
   - Provides setter methods to update displayed values dynamically.

   Classes:
   - DigitalDisplay: A QWidget subclass that renders a digital-style display.

   Usage Example:
       display = DigitalDisplay()
       display.setPresetText("Grand Piano")
       display.setPresetNumber(12)
       display.setProgramText("User Program 1")
       display.setProgramNumber(5)
       display.setOctave(1)

   Dependencies:
   - PySide6.QtWidgets (QWidget, QSizePolicy)
   - PySide6.QtGui (QPainter, QColor, QPen, QFont)



Classes
-------

.. autoapisummary::

   display.digital.DigitalDisplayBase
   display.digital.DigitalTitle
   display.digital.DigitalDisplay


Module Contents
---------------

.. py:class:: DigitalDisplayBase(digital_font_family: str = 'JD LCD Rounded', parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Base class for JD-Xi style digital displays.


   .. py:attribute:: digital_font_family
      :value: 'JD LCD Rounded'



   .. py:attribute:: display_texts
      :value: []



   .. py:method:: paintEvent(event: PySide6.QtGui.QPaintEvent) -> None

      Handles rendering of the digital display.



   .. py:method:: draw_display(painter: PySide6.QtGui.QPainter)

      Draws the LCD-style display with a gradient glow effect.



   .. py:method:: update_display(texts: list) -> None

      Update the display text and trigger repaint.

      :param texts: list



   .. py:method:: set_upper_display_text(text: str) -> None

      Update the display text and trigger repaint.

      :param text: list



.. py:class:: DigitalTitle(tone_name: str = 'Init Tone', digital_font_family: str = 'JD LCD Rounded', show_upper_text: bool = True, parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`DigitalDisplayBase`


   Simplified display showing only the current tone name.


   .. py:attribute:: show_upper_text
      :value: True



   .. py:method:: __del__()


   .. py:method:: set_tone_name(tone_name: str) -> None

      Update the tone name display.

      :param tone_name: str



   .. py:property:: text
      :type: str



   .. py:method:: setText(value: str) -> None

      Alias for set_tone_name.

      :param value: str



.. py:class:: DigitalDisplay(current_octave: int = 0, digital_font_family: str = 'JD LCD Rounded', active_synth: str = 'D1', tone_name: str = 'Init Tone', tone_number: int = 1, program_name: str = 'Init Program', program_bank_letter: str = 'A', program_number: int = 1, parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`DigitalDisplayBase`


   Digital LCD-style display widget.


   .. py:attribute:: active_synth
      :value: 'D1'



   .. py:attribute:: digital_font_family
      :value: 'JD LCD Rounded'



   .. py:attribute:: current_octave
      :value: 0



   .. py:attribute:: tone_name
      :value: 'Init Tone'



   .. py:attribute:: tone_number
      :value: 1



   .. py:attribute:: program_name
      :value: 'Init Program'



   .. py:attribute:: program_number
      :value: 1



   .. py:attribute:: program_bank_letter
      :value: 'A'



   .. py:attribute:: program_id
      :value: 'A'



   .. py:attribute:: margin
      :value: 10



   .. py:method:: paintEvent(event: PySide6.QtGui.QPaintEvent) -> None

      Handles the rendering of the digital display.

      :param event: QPaintEvent



   .. py:method:: draw_display(painter: PySide6.QtGui.QPainter)

      Draws the JD-Xi style digital display with a gradient glow effect.



   .. py:method:: setPresetText(text: str) -> None

      Set preset name and trigger repaint.

      :param text: str



   .. py:method:: setPresetNumber(number: int) -> None

      Set preset number and trigger repaint.

      :param number: int



   .. py:method:: setProgramText(text: str) -> None

      Set program name and trigger repaint.

      :param text: str



   .. py:method:: setProgramNumber(number: int) -> None

      Set program number and trigger repaint.

      :param number: int



   .. py:method:: setOctave(octave: int) -> None

      Set current octave and trigger repaint.

      :param octave: int



   .. py:method:: repaint_display(current_octave: int, tone_number: int, tone_name: str, program_name: str, active_synth: str = 'D1') -> None


   .. py:method:: _update_display(synth_type, digital1_tone_name, digital2_tone_name, drums_tone_name, analog_tone_name, tone_number, tone_name, program_name, program_number, program_bank_letter='A')

      Update the JD-Xi display image.

      :param synth_type: str
      :param digital1_tone_name: str
      :param digital2_tone_name: str
      :param drums_tone_name: str
      :param analog_tone_name: str



