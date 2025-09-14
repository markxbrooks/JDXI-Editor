slider
======

.. py:module:: slider


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/slider/slider/index


Classes
-------

.. autoapisummary::

   slider.Slider


Package Contents
----------------

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



