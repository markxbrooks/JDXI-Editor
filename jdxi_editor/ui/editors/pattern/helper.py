from PySide6.QtWidgets import QPushButton, QSpinBox

from jdxi_editor.ui.editors.midi_player.transport.spec import NoteButtonSpec
from jdxi_editor.ui.editors.pattern.models import NoteButtonAttrs
from jdxi_editor.ui.widgets.pattern.measure import PatternMeasure
from jdxi_editor.ui.widgets.pattern.sequencer_button import SequencerButton


def reset_button(button: SequencerButton):
    """reset the Sequencer button"""
    button.row = button.row  # or keep as is if you really want to preserve
    # If you want to reset the local column as well, assign explicitly
    # button.column = button.column
    button.note = None
    button.note_duration = None
    button.note_velocity = None
    button.note_spec = NoteButtonSpec()
    update_button_state(button, False)


def reset_measure(measure: PatternMeasure):
    for r in range(4):
        for btn in measure.buttons[r]:
            reset_button(btn)


def get_button_note_spec(button) -> NoteButtonSpec:
    """Return the effective NoteButtonSpec for a step button (from attribute or built from NOTE/NOTE_DURATION/NOTE_VELOCITY)."""
    spec = getattr(button, "note_spec", None)
    if spec is not None:
        return spec
    return NoteButtonSpec(
        note=getattr(button, NoteButtonAttrs.NOTE, None),
        duration_ms=int(getattr(button, NoteButtonAttrs.NOTE_DURATION, 120) or 120),
        velocity=getattr(button, NoteButtonAttrs.NOTE_VELOCITY, 100) or 100,
    )


def sync_button_note_spec(button) -> None:
    """Update button.note_spec from NOTE, NOTE_DURATION, NOTE_VELOCITY."""
    button.note_spec = NoteButtonSpec(
        note=getattr(button, NoteButtonAttrs.NOTE, None),
        duration_ms=int(getattr(button, NoteButtonAttrs.NOTE_DURATION, 120) or 120),
        velocity=getattr(button, NoteButtonAttrs.NOTE_VELOCITY, 100) or 100,
    )


def update_button_state(
    button: QPushButton, checked_state: bool = None, enabled_state: bool = None
):
    """update button state"""
    button.blockSignals(True)
    if enabled_state is not None:
        button.setEnabled(enabled_state)
    if checked_state is not None:
        button.setChecked(checked_state)
    button.blockSignals(False)


def set_spinbox_value(spinbox: QSpinBox, value: int):
    """set spinbox value safely"""
    spinbox.blockSignals(True)
    spinbox.setValue(value)
    spinbox.blockSignals(False)
