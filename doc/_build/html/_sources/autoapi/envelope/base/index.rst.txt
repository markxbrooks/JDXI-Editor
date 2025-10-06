envelope.base
=============

.. py:module:: envelope.base


Attributes
----------

.. autoapisummary::

   envelope.base.TOOLTIPS


Classes
-------

.. autoapisummary::

   envelope.base.EnvelopeWidgetBase


Module Contents
---------------

.. py:data:: TOOLTIPS

.. py:class:: EnvelopeWidgetBase(parameters: list[jdxi_editor.midi.data.parameter.AddressParameter], envelope_keys: list[str], create_parameter_slider: Callable, midi_helper: Optional[jdxi_editor.midi.io.helper.MidiIOHelper] = None, address: Optional[jdxi_editor.midi.data.address.address.RolandSysExAddress] = None, controls: Optional[dict[jdxi_editor.midi.data.parameter.AddressParameter, jdxi_editor.ui.widgets.slider.Slider]] = None, parent: Optional[PySide6.QtWidgets.QWidget] = None)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   Base class for envelope widgets in the JD-Xi editor


   .. py:attribute:: envelope_changed


   .. py:attribute:: plot
      :value: None



   .. py:attribute:: address
      :value: None



   .. py:attribute:: midi_helper
      :value: None



   .. py:attribute:: controls


   .. py:attribute:: envelope


   .. py:attribute:: _create_parameter_slider


   .. py:attribute:: _params


   .. py:attribute:: _keys


   .. py:attribute:: _control_widgets
      :value: []



   .. py:method:: setEnabled(enabled: bool)


   .. py:method:: update()

      Update the envelope values and plot



   .. py:method:: set_values(envelope: dict) -> None

      Update envelope values and trigger address redraw

      :param envelope: dict
      :return: None



   .. py:method:: emit_envelope_changed() -> None

      Emit the envelope changed signal

      :return: None



   .. py:method:: update_envelope_from_controls() -> None

      Update envelope values from slider controls.

      :return:



   .. py:method:: update_controls_from_envelope() -> None

      Update slider controls from envelope values.

      :return: None



