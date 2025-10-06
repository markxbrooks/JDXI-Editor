jdxi_editor.midi.message.effects.vocal
======================================

.. py:module:: jdxi_editor.midi.message.effects.vocal

.. autoapi-nested-parse::

   VocalEffectMessage
   ==================

   # Example usage:
   # Set vocal effect level
   >>> msg = VocalEffectMessage(param=VocalEffect.LEVEL.value, value=100)  # Level 100

   # Set auto pitch parameters
   >>> msg = VocalEffectMessage(param=VocalEffect.AUTO_PITCH_SW.value, value=1)  # ON

   >>> msg = VocalEffectMessage(param=VocalEffect.AUTO_PITCH_TYPE.value, value=0)  # SOFT

   # Set vocoder parameters
   >>> msg = VocalEffectMessage(param=VocalEffect.VOCODER_SW.value, value=1)  # ON

   >>> msg = VocalEffectMessage(param=VocalEffect.VOCODER_ENV.value, value=1)  # SOFT



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.message.effects.vocal.VocalEffectMessage


Module Contents
---------------

.. py:class:: VocalEffectMessage

   Bases: :py:obj:`jdxi_editor.midi.message.roland.RolandSysEx`


   Program Vocal Effect parameter message


   .. py:attribute:: command
      :type:  int


   .. py:attribute:: area
      :type:  int


   .. py:attribute:: section
      :type:  int
      :value: 1



   .. py:attribute:: group
      :type:  int
      :value: 0



   .. py:attribute:: lsb
      :type:  int
      :value: 0



   .. py:attribute:: value
      :type:  int
      :value: 0



   .. py:method:: __post_init__()

      Set up address and data



