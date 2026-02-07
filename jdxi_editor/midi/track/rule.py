"""
Re-export track classification rules from classification module to avoid circular imports.
Rule definitions live in classification.py; this module exists for backward compatibility.
"""

from jdxi_editor.midi.track.classification import (
    BASS_RULES,
    KEYS_RULES,
    STRINGS_RULES,
    ScoreRule,
)

__all__ = ["BASS_RULES", "KEYS_RULES", "STRINGS_RULES", "ScoreRule"]
