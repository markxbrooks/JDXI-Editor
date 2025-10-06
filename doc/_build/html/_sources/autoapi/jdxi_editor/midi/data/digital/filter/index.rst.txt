jdxi_editor.midi.data.digital.filter
====================================

.. py:module:: jdxi_editor.midi.data.digital.filter

.. autoapi-nested-parse::

   Digital Filter



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.digital.filter.DigitalFilterMode
   jdxi_editor.midi.data.digital.filter.DigitalFilterSlope


Module Contents
---------------

.. py:class:: DigitalFilterMode

   Bases: :py:obj:`enum.Enum`


   Filter mode types


   .. py:attribute:: BYPASS
      :value: 0



   .. py:attribute:: LPF
      :value: 1



   .. py:attribute:: HPF
      :value: 2



   .. py:attribute:: BPF
      :value: 3



   .. py:attribute:: PKG
      :value: 4



   .. py:attribute:: LPF2
      :value: 5



   .. py:attribute:: LPF3
      :value: 6



   .. py:attribute:: LPF4
      :value: 7



   .. py:property:: display_name
      :type: str


      Get display name for filter mode


.. py:class:: DigitalFilterSlope

   Bases: :py:obj:`enum.Enum`


   Filter slope values


   .. py:attribute:: DB_12
      :value: 0



   .. py:attribute:: DB_24
      :value: 1



   .. py:property:: display_name
      :type: str


      Get display name for filter slope


