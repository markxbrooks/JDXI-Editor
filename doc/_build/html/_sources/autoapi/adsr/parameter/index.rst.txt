adsr.parameter
==============

.. py:module:: adsr.parameter

.. autoapi-nested-parse::

   ADSR Parameter Enum



Classes
-------

.. autoapisummary::

   adsr.parameter.ADSRParameter


Module Contents
---------------

.. py:class:: ADSRParameter

   Bases: :py:obj:`enum.Enum`


   Generic enumeration.

   Derive from this class to define new enumerations.


   .. py:attribute:: ATTACK_TIME
      :value: 'attack_time'



   .. py:attribute:: DECAY_TIME
      :value: 'decay_time'



   .. py:attribute:: SUSTAIN_LEVEL
      :value: 'sustain_level'



   .. py:attribute:: RELEASE_TIME
      :value: 'release_time'



   .. py:attribute:: INITIAL_LEVEL
      :value: 'initial_level'



   .. py:attribute:: PEAK_LEVEL
      :value: 'peak_level'



   .. py:method:: __str__() -> str

      Return the string representation of the parameter.
      :return: str



