jdxi_editor.ui.editors.pattern.measure
======================================

.. py:module:: jdxi_editor.ui.editors.pattern.measure

.. autoapi-nested-parse::

   extract_measure
   ===============

   Extracts a single measure from a midi file.

   Example usage
   =============
   >>>midi_file = 'your_midi_file.mid'  # Replace with your MIDI file path
   ...measure_to_extract = 2  # Extract notes from the second measure
   ...extracted_notes = extract_measure(midi_file, measure_to_extract)

   >>>print(f"Notes in measure {measure_to_extract}:")
   ...for note in extracted_notes:
   ...   print(note)



Functions
---------

.. autoapisummary::

   jdxi_editor.ui.editors.pattern.measure.extract_measure


Module Contents
---------------

.. py:function:: extract_measure(midi_file_path, measure_number)

   Extracts notes from a specific measure of a MIDI file.


