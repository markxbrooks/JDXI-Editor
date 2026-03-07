"""
Export a MIDI file to sheet music PDF (music21 + LilyPond) for use by the app menu.
Uses the same logic as piano.py for consistent LilyPond behavior.
"""

import shutil
import time
import warnings
from pathlib import Path
from typing import Any, Optional

from decologr import Decologr as log
from music21 import (
    Music21Object,
    chord,
    converter,
    environment,
)
from music21 import instrument as m21_instrument
from music21 import (
    metadata,
    note,
    stream,
)
from music21.stream import Measure, Opus, Part, Score, Stream

from jdxi_editor.midi.music.track import get_track_names


def short_name(name: str, max_len: int = 12) -> str:
    """Abbreviation for staff label (e.g. 'Piano' -> 'Pno.', long names truncated)."""
    if not name or len(name) <= max_len:
        return name or ""
    return name[: max_len - 1].rstrip() + "."


def export_midi_to_pdf(midi_path: str | Path) -> Optional[str]:
    """
    Export a MIDI file to a PDF in the same directory (stem.pdf).
    Mirrors piano.main() for consistent LilyPond behavior. Returns the PDF path or None on failure.
    """
    midi_path = Path(midi_path)
    if not midi_path.exists():
        return None
    try:
        env = environment.UserSettings()
        lily_path = env.get("lilypondPath")
        if lily_path:
            env["lilypondPath"] = lily_path
    except Exception:
        pass

    midi_file_stem = midi_path.stem
    filename_parts = midi_file_stem.split(" - ")
    title = filename_parts[0]
    composer = filename_parts[1] if len(filename_parts) > 1 else ""

    # Parse the MIDI file
    score = converter.parse(str(midi_path))
    # Single-track MIDI can return a Part; wrap so we always have score.parts
    if not hasattr(score, "parts") or score.parts is None:
        wrapped = stream.Score()
        wrapped.insert(0, score)
        score = wrapped

    # --- Set metadata ---
    score.metadata = metadata.Metadata()
    score.metadata.title = title
    score.metadata.composer = composer

    # --- Get MIDI track names for staff labels ---
    track_names = get_track_names(str(midi_path))

    # Annotate each staff with its MIDI track name (for PDF labels)
    for idx, part in enumerate(score.parts):
        track_name = None
        if idx < len(track_names):
            track_name = track_names[idx]
        if not track_name:
            inst = part.getInstrument()
            track_name = inst.instrumentName if inst else f"Part {idx + 1}"
        part.partName = track_name
        # So LilyPond prints the label on the staff, set the Instrument name too
        inst = part.getInstrument()
        if inst is not None:
            inst.instrumentName = track_name
            inst.instrumentAbbreviation = short_name(track_name)
        else:
            part.insert(0, m21_instrument.Instrument(instrumentName=track_name))

    # Count notes before processing
    note_count_before = len(list(score.recurse().notes))
    log.message(f"Score has {note_count_before} notes before processing")
    
    # Try quantization, but skip if it empties the score
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            quantized = score.quantize(quarterLengthDivisors=(4, 3))
            note_count_after = len(list(quantized.recurse().notes))
            if note_count_after > 0:
                score = quantized
                log.message(f"Quantization preserved {note_count_after} notes")
            else:
                log.warning("Quantization emptied score, using original")
        except Exception as e:
            log.warning(f"Quantization failed, using original: {e}")
    
    # Make measures and notation
    try:
        score.makeMeasures(inPlace=True)
        score.makeNotation(inPlace=True)
    except Exception as e:
        log.warning(f"Notation processing issue (continuing anyway): {e}")

    # Validate score has content before writing
    final_note_count = len(list(score.recurse().notes))
    if final_note_count == 0:
        log.error(scope="pdf_export", message="Score has no notes after processing - cannot create PDF")
        return None
    
    log.message(f"Writing score with {final_note_count} notes to LilyPond")
    
    # Safe output file name (same as piano.py)
    safe_output = midi_path.parent / "output_score"
    final_file = midi_path.parent / f"{midi_file_stem}.pdf"

    # Write PDF via Lilypond - capture the actual output path
    # music21 may raise LilyTranslateException even if LilyPond succeeded
    result_path = None
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result_path = score.write(fp=safe_output, fmt="lily.pdf")
    except Exception as e:
        # LilyPond may have succeeded even if music21 can't find the output
        # Log the error but continue to search for the PDF
        log.warning(f"music21 exception (may still find PDF): {e}")
    
    # Give LilyPond a moment to finish writing the file
    time.sleep(0.2)
    
    # Check for PDF in multiple possible locations
    possible_pdfs = [
        Path(result_path) if result_path else None,  # Path returned by music21
        safe_output.with_suffix(".pdf"),              # Expected location
        Path(str(safe_output) + ".pdf"),              # Alternative naming
        midi_path.parent / "output_score.pdf",        # Direct path
    ]
    
    # Also search for any PDF created recently in the directory
    recent_pdfs = list(midi_path.parent.glob("output_score*.pdf"))
    for pdf in recent_pdfs:
        if pdf not in possible_pdfs:
            possible_pdfs.append(pdf)
    
    for safe_pdf in possible_pdfs:
        if safe_pdf and safe_pdf.exists():
            log.message(f"Found PDF at: {safe_pdf}")
            shutil.move(str(safe_pdf), str(final_file))
            return str(final_file)
    
    # Log what we couldn't find for debugging
    log.error(
        scope="pdf_export",
        message=f"Could not find PDF. Checked: {[str(p) for p in possible_pdfs if p]}"
    )
    return None


def cleanup_score(score: Score | Part | Opus) -> Stream[Music21Object | Any] | None:
    """Minimal cleanup with safe quantization."""
    # Try quantization, but skip if it empties the score
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            quantized = score.quantize(quarterLengthDivisors=(4, 3))
            note_count_after = len(list(quantized.recurse().notes))
            if note_count_after > 0:
                score = quantized
            else:
                log.warning("Quantization emptied score, using original")
        except Exception as e:
            log.warning(f"Quantization failed: {e}")
    
    try:
        score.makeMeasures(inPlace=True)
        score.makeNotation(inPlace=True)
    except Exception as e:
        log.warning(f"Notation processing issue: {e}")
    
    return score


def annotate_staffs(score: Score | Part | Opus, track_names: list[str]):
    # Annotate each staff with its MIDI track name (for PDF labels)
    # Add more guards to handle the case where the part is None
    for idx, part in enumerate(score.parts):
        if part is None:
            continue
        track_name = None
        if idx < len(track_names):
            track_name = track_names[idx]
        if not track_name or track_name == "" or track_name is None:
            inst = part.getInstrument()
            track_name = inst.instrumentName if inst else f"Part {idx + 1}"
        part.partName = track_name
        # So LilyPond prints the label on the staff, set the Instrument name too
        inst = part.getInstrument()
        if inst is not None:
            inst.instrumentName = track_name
            inst.instrumentAbbreviation = short_name(track_name)
        else:
            part.insert(0, m21_instrument.Instrument(instrumentName=track_name))


def _ensure_parts_have_measures(score: stream.Score) -> None:
    """Ensure every part has at least one Measure so LilyPond export does not hit context bugs."""
    for part in score.parts:
        if part is None:
            continue
        measures = list(part.getElementsByClass(Measure))
        if not measures:
            # Part has no measures; add one whole rest and re-run makeMeasures for this part
            r = note.Rest(quarterLength=4)
            part.insert(0, r)
            part.makeMeasures(inPlace=True)


def export_score(midi_file: Path, midi_file_stem: str, score) -> tuple[Path, Path]:
    # LilyPond exporter can crash if score has no parts or broken structure
    parts = getattr(score, "parts", None)
    if parts is None or (hasattr(parts, "__len__") and len(score.parts) == 0):
        raise ValueError(
            "Score has no parts (all tracks may be empty). "
            "LilyPond export requires at least one part with notes."
        )

    _ensure_parts_have_measures(score)

    # Safe output file name
    safe_output = midi_file.parent / "output_score"

    result_path = None
    try:
        result_path = score.write(fp=safe_output, fmt="lily.pdf")
    except AttributeError as e:
        if "append" in str(e) or "contents" in str(e).lower():
            raise ValueError(
                "LilyPond export failed due to score structure (music21/LilyPond quirk). "
                "Try a simpler MIDI file or export from another tool."
            ) from e
        raise
    except Exception as e:
        # LilyPond may have succeeded even if music21 can't find the output
        log.warning(f"music21 exception (may still find PDF): {e}")

    # Give LilyPond a moment to finish writing the file
    time.sleep(0.2)

    # Find the actual PDF - check multiple possible locations
    actual_pdf = None
    possible_pdfs = [
        Path(result_path) if result_path else None,
        safe_output.with_suffix(".pdf"),
        Path(str(safe_output) + ".pdf"),
        midi_file.parent / "output_score.pdf",
    ]
    
    # Also search for any PDF created recently in the directory
    recent_pdfs = list(midi_file.parent.glob("output_score*.pdf"))
    for pdf in recent_pdfs:
        if pdf not in possible_pdfs:
            possible_pdfs.append(pdf)
    
    for pdf_path in possible_pdfs:
        if pdf_path and pdf_path.exists():
            actual_pdf = pdf_path
            break
    
    if actual_pdf:
        log.message("PDF created:", actual_pdf)
    else:
        log.warning(f"PDF not found at expected locations: {[str(p) for p in possible_pdfs if p]}")

    final_file = midi_file.parent / f"{midi_file_stem}.pdf"
    return final_file, actual_pdf or safe_output


def set_metadata(composer: str, score: Score | Part | Opus, title: str):
    # --- Set metadata ---
    score.metadata = metadata.Metadata()
    score.metadata.title = title
    score.metadata.composer = composer


def remove_empty_parts(score: stream.Score):
    """
    Remove any parts that have no notes, chords, or rests.
    Returns a cleaned score.
    """
    for part in score.parts[:]:  # copy the list so we can remove safely
        has_music = any(
            isinstance(e, (note.Note, note.Rest, chord.Chord)) for e in part.recurse()
        )
        if not has_music:
            log.message(f"Removing empty part: {part.partName}")
            score.remove(part)
    return score
