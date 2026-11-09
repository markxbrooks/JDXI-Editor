#!/usr/bin/env python3
"""Compatibility entry point for the MIDI part classifier.

Implementation lives in midi_parts. Names stay importable from this module,
and `python scripts/classify_midi_parts.py` still dispatches the CLI.
"""

from __future__ import annotations

import sys
from pathlib import Path

_scripts = str(Path(__file__).resolve().parent)
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

from midi_parts.models import (
    DRUM_CHANNEL,
    GHOST,
    Note,
    RefNote,
    Grid,
    Result,
)

from midi_parts.midi_io import (
    _paired_notes,
    _tempo_map,
    _seconds,
    _ticks,
    load_transcription,
    load_reference,
    part_order,
    write_midi,
    write_csv,
    write_piano_roll,
    mmss,
)

from midi_parts.audio import (
    CHORD_HOP,
    chroma_frames,
    load_wav_mono,
    have_librosa,
    audio_chroma,
    _cqt_chroma,
    _fft_chroma,
    fold_chroma,
    _fft_semitones,
    _unit_rows,
    audio_offset,
    blend_chroma,
)

from midi_parts.alignment import (
    FRAME_S,
    _onset_chroma,
    align_reference,
    match_reference,
)

from midi_parts.classification import (
    RULE_PARTS,
    GROUP_S,
    PITCH_SMOOTHING,
    merge_fragments,
    mark_ghosts,
    estimate_grid,
    find_sections,
    _groups,
    trace_lines,
    add_context,
    _features,
    _train_profiles,
    _max_polyphony,
    _profile_scores,
    _classify_profile,
    enforce_polyphony,
    rule_label,
    constraint_fit,
    apply_part_constraints,
    label_remaining,
    apply_corrections,
    classify,
    report,
    run_classify,
)

from midi_parts.chords import (
    PITCH_NAMES,
    _ROOTS,
    CHORD_QUALITIES,
    NO_CHORD,
    ChordSpan,
    parse_chord,
    chord_name,
    chord_vocabulary,
    detect_chords,
    voice_chord,
    ChordResult,
    rebuild_chords,
    write_chord_midi,
    run_chords,
)

from midi_parts.tempo import (
    BEATS_PER_BAR,
    TempoPlan,
    grid_coherence,
    fit_steady_grid,
    steady_region,
    _bars_from_chart,
    _fill_bars,
    plan_tempo,
    steady_start_tick,
)

from midi_parts.rhythm import (
    STRAIGHT_DIVISIONS,
    TRIPLET_DIVISIONS,
    subdivision_fits,
    _grid_scores,
    swing_ratio,
    BarRhythm,
    bar_rhythms,
    rhythm_runs,
    run_rhythm,
)

from midi_parts.quantize import (
    QuantizeStats,
    quantize_midi,
    run_quantize,
)

from midi_parts.roundtrip import (
    ROUNDTRIP_LOW,
    ROUNDTRIP_HIGH,
    notes_semitones,
    _shift,
    RoundTrip,
    roundtrip_scores,
    _render_copy,
    write_correlation_histogram,
    run_roundtrip,
)

from midi_parts.accuracy import (
    TNote,
    Accuracy,
    load_notes,
    dedupe,
    match_notes,
    best_offset,
    frame_f,
    wrong_kind,
    accuracy,
    run_accuracy,
)

from midi_parts.key import (
    KEY_PROFILES,
    SCALES,
    Key,
    pitch_class_profile,
    detect_key,
    parse_key,
    _parse_pitch_classes,
    _note_rows,
    run_key,
    _chord_at,
    _read_chart,
    run_filter_key,
)

from midi_parts.patterns import (
    REVIEW_CHANNEL,
    GridNote,
    _grid_notes,
    _bar_similarity,
    PatternChange,
    repair_patterns,
    write_pattern_midi,
    run_patterns,
)

from midi_parts.cycles import (
    Cycle,
    _step_notes,
    self_alignment,
    find_cycle_period,
    _consensus,
    _instance_agreement,
    find_cycles,
    cycle_from_run,
    finish_cycles,
    repair_cycles,
    MIN_CONFIDENCE,
    MIN_CONSERVATION,
    FIX_PITCH_CONFIDENCE,
    repeat_logo,
    describe_logo,
    describe_cycle,
    run_cycles,
)

from midi_parts.merge import (
    load_source,
    merge_transcriptions,
    run_merge,
)

from midi_parts.cli import (
    SOUNDFONT,
    _script_module,
    _midi_patterns,
    run_repeats,
    run_gates,
    run_musicality,
    run_diagnose,
    run_render_test,
    run_evaluate,
    main,
)

if __name__ == "__main__":
    sys.exit(main())
