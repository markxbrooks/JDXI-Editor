slider.slider
=============

.. py:module:: slider.slider

.. autoapi-nested-parse::

   Custom Slider Widget Module

   This module defines address custom slider widget (Slider) that combines address QSlider with address label and address value display.
   It offers additional functionality including:

   - Customizable value display using address format function.
   - Support for vertical or horizontal orientation.
   - Option to add address visual center mark for bipolar sliders.
   - Customizable tick mark positions and intervals.
   - Integrated signal (valueChanged) for reacting to slider value changes.

   The widget is built using PySide6 and is intended for use in applications requiring address more informative slider,
   such as in audio applications or other UIs where real-time feedback is important.

   Usage Example:
       from your_module import Slider
       slider = Slider("Volume", 0, 100, vertical=False)
       slider.setValueDisplayFormat(lambda v: f"{v}%")
       slider.valueChanged.connect(handle_value_change)

   This module requires PySide6 to be installed.



Classes
-------

.. autoapisummary::

   slider.slider.Slider


Module Contents
---------------

.. py:class:: Slider(label: str, min_value: int, max_value: int, midi_helper: jdxi_editor.midi.io.helper.MidiIOHelper, vertical: bool = False, show_value_label: bool = True, is_bipolar: bool = False, tooltip: str = '', draw_center_mark: bool = True, draw_tick_marks: bool = True, initial_value: int = 0, parent=None)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Custom slider widget with label and value display


   .. py:attribute:: rpn_slider_changed


   .. py:class:: TickPosition

      .. py:attribute:: NoTicks


      .. py:attribute:: TicksBothSides


      .. py:attribute:: TicksAbove


      .. py:attribute:: TicksBelow


      .. py:attribute:: TicksLeft


      .. py:attribute:: TicksRight



   .. py:attribute:: valueChanged


   .. py:attribute:: label


   .. py:attribute:: min_value


   .. py:attribute:: max_value


   .. py:attribute:: midi_helper


   .. py:attribute:: value_display_format


   .. py:attribute:: has_center_mark
      :value: False



   .. py:attribute:: center_value
      :value: 0



   .. py:attribute:: vertical
      :value: False



   .. py:attribute:: is_bipolar
      :value: False



   .. py:attribute:: draw_center_mark
      :value: True



   .. py:attribute:: draw_tick_marks
      :value: True



   .. py:attribute:: slider


   .. py:attribute:: value_label


   .. py:method:: setLabel(text: str)


   .. py:method:: setValueDisplayFormat(format_func)

      Set custom format function for value display



   .. py:method:: setCenterMark(center_value)

      Set center mark for bipolar sliders



   .. py:method:: _on_valueChanged(value: int)

      Handle slider value changes



   .. py:method:: _update_value_label()

      Update the value label using current format function



   .. py:method:: paintEvent(event)

      Override paint event to draw center mark if needed



   .. py:method:: value() -> int

      Get current value



   .. py:method:: setValue(value: int)

      Set current value



   .. py:method:: setEnabled(enabled: bool)

      Set enabled state



   .. py:method:: setTickPosition(position)

      Set the tick mark position on the slider



   .. py:method:: setTickInterval(interval)

      Set the interval between tick marks



