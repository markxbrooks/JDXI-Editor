jdxi_editor.ui.editors.config
=============================

.. py:module:: jdxi_editor.ui.editors.config

.. autoapi-nested-parse::

   Configuration of Editor classes for the JDXI Editor.

   Stores
   -Title: The title of the editor.
   -Editor Class: The class that implements the editor functionality.
   -Synth Type: Optional type of synthesizer associated with the editor.
   -MIDI Channel: Optional MIDI channel for the editor.
   -icon: Icon for the editor, represented as a string.
   -Keyword Arguments: Additional parameters for the editor.


   Example usage:
   "arpeggio": EditorConfig(
       title="Arpeggiator",
       editor_class=ArpeggioEditor,
       icon="ph.music-notes-simple-bold"
   ),



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.config.EditorConfig


Module Contents
---------------

.. py:class:: EditorConfig

   .. py:attribute:: title
      :type:  str


   .. py:attribute:: editor_class
      :type:  jdxi_editor.ui.editors.synth.base.SynthBase


   .. py:attribute:: synth_type
      :type:  Optional[Any]
      :value: None



   .. py:attribute:: midi_channel
      :type:  Optional[Any]
      :value: None



   .. py:attribute:: kwargs
      :type:  Dict[str, Any]


   .. py:attribute:: icon
      :type:  str
      :value: ''



