button.channel
==============

.. py:module:: button.channel

.. autoapi-nested-parse::

   Channel Button



Classes
-------

.. autoapisummary::

   button.channel.ChannelButton


Module Contents
---------------

.. py:class:: ChannelButton(parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`PySide6.QtWidgets.QPushButton`


   Channel indicator button with synth-specific styling


   .. py:attribute:: CHANNEL_STYLES


   .. py:attribute:: current_channel
      :value: 0



   .. py:method:: set_channel(channel: int) -> None

      Set channel and update appearance

      :param channel: int



   .. py:method:: _update_style() -> None

      Update button appearance based on channel

      :return: None



