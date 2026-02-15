"""
Export a MIDI file to sheet music PDF (music21 + LilyPond) for use by the app menu.
Uses the same logic as piano.py for consistent LilyPond behavior.
"""

import shutil
from pathlib import Path
from typing import Optional, Any

from music21 import (
    converter,
    environment,
    instrument as m21_instrument,
    metadata,
    stream,
    Music21Object,
    note,
    chord,
)
from music21.stream import Score, Part, Opus, Stream, Measure

from decologr import Decologr as log
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

    # Minimal cleanup
    score = score.quantize(quarterLengthDivisors=(4, 3))
    score.makeMeasures(inPlace=True)
    score.makeNotation(inPlace=True)

    # Safe output file name (same as piano.py)
    safe_output = midi_path.parent / "output_score"

    # Write PDF via Lilypond
    score.write(fp=safe_output, fmt="lily.pdf")

    final_file = midi_path.parent / f"{midi_file_stem}.pdf"
    safe_pdf = safe_output.with_suffix(".pdf")
    if safe_pdf.exists():
        shutil.move(str(safe_pdf), str(final_file))
        return str(final_file)
    return None


def cleanup_score(score: Score | Part | Opus) -> Stream[Music21Object | Any] | None:
    # Minimal cleanup
    score = score.quantize(quarterLengthDivisors=(4, 3))
    score.makeMeasures(inPlace=True)
    score.makeNotation(inPlace=True)
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

    try:
        score.write(fp=safe_output, fmt="lily.pdf")
    except AttributeError as e:
        if "append" in str(e) or "contents" in str(e).lower():
            raise ValueError(
                "LilyPond export failed due to score structure (music21/LilyPond quirk). "
                "Try a simpler MIDI file or export from another tool."
            ) from e
        raise

    log.message("PDF created:", safe_output.with_suffix(".pdf"))

    final_file = midi_file.parent / f"{midi_file_stem}.pdf"
    return final_file, safe_output


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
        has_music = any(isinstance(e, (note.Note, note.Rest, chord.Chord))
                        for e in part.recurse())
        if not has_music:
            log.message(f"Removing empty part: {part.partName}")
            score.remove(part)
    return score