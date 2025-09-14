jdxi_editor.midi.data.analog.filter
===================================

.. py:module:: jdxi_editor.midi.data.analog.filter

.. autoapi-nested-parse::

   Analog Filter



Attributes
----------

.. autoapisummary::

   jdxi_editor.midi.data.analog.filter.ANALOG_FILTER_GROUP


Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.analog.filter.FilterType
   jdxi_editor.midi.data.analog.filter.AnalogFilterType


Module Contents
---------------

.. py:data:: ANALOG_FILTER_GROUP
   :value: 1


.. py:class:: FilterType

   Bases: :py:obj:`enum.IntEnum`


   Analog filter types


   .. py:attribute:: LPF
      :value: 0



   .. py:attribute:: HPF
      :value: 1



   .. py:attribute:: BPF
      :value: 2



   .. py:attribute:: PKG
      :value: 3



.. py:class:: AnalogFilterType

   Bases: :py:obj:`enum.Enum`


   Analog filter types


   .. py:attribute:: BYPASS
      :value: 0



   .. py:attribute:: LPF
      :value: 1



