"""
Undo, redo and reload for one tone editor.

A change is recorded where a control sends a parameter. A drag of one slider
is one step. A value applied with the control's signals blocked came from the
JD-Xi, so it is not a step: it becomes the value undo returns to. Reload puts
back every value as it was before its first change.
"""

from __future__ import annotations

import time
from typing import Optional

from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

MERGE_SECONDS = 1.0  # changes of one control closer than this are one step (a drag)
MAX_STEPS = 30


def _parent_widget(widget):
    """The Qt parent. SynthBase stores the constructor parent on ``parent``, which hides the method."""
    parent_widget = getattr(widget, "parentWidget", None)
    if callable(parent_widget):
        found = parent_widget()
        if found is not None:
            return found
    parent = getattr(widget, "parent", None)
    if callable(parent):
        return parent()
    return None


def history_of(widget) -> Optional["EditHistory"]:
    """The EditHistory of *widget* or one of its parents."""
    current = widget
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        found = getattr(current, "history", None)
        if isinstance(found, EditHistory):
            return found
        current = _parent_widget(current)
    return None


def note_external_value(widget) -> None:
    """A value arrived with the control's signals blocked: the JD-Xi, not an edit."""
    history = history_of(widget)
    if history is not None and not history.replaying:
        history.external_change(widget)


def shown_value(widget) -> int:
    """The value a control shows, the same number its valueChanged signal sends."""
    reader = getattr(widget, "edit_value", None)
    value = reader() if callable(reader) else widget.value()
    return int(round(float(value)))


class _Edit:
    __slots__ = ("changes", "time")

    def __init__(self, widget, old: int, new: int):
        self.changes = {widget: [old, new]}
        self.time = time.monotonic()

    def record(self, widget, old: int, new: int) -> None:
        change = self.changes.get(widget)
        if change is None:
            if old != new:
                self.changes[widget] = [old, new]
            return
        change[1] = new
        if change[0] == new:
            del self.changes[widget]


class EditHistory:
    """The user's changes to one editor's controls."""

    def __init__(self, editor: QWidget):
        self.editor = editor
        self._undo: list[_Edit] = []
        self._redo: list[_Edit] = []
        self._origin: dict = {}  # control -> what it showed before the first change
        self._replaying = False
        self._sealed = True
        self._group_depth = 0
        self._group: Optional[_Edit] = None
        self._modified = False
        self._on_state = (
            []
        )  # callables, so the buttons follow without a QObject of their own
        self._on_modified = []

    @property
    def replaying(self) -> bool:
        return self._replaying

    def on_state(self, callback) -> None:
        self._on_state.append(callback)

    def on_modified(self, callback) -> None:
        self._on_modified.append(callback)

    # ---------------------------------------------------------------- recording
    def record(self, widget, old: int, new: int) -> None:
        """One user change of *widget*, from *old* to *new*."""
        if self._replaying or old == new:
            return
        self._origin.setdefault(widget, old)
        if self._group_depth:
            if self._group is None:
                self._group = _Edit(widget, old, new)
            else:
                self._group.record(widget, old, new)
            self._update()
            return
        top = self._undo[-1] if self._undo else None
        if (
            top is not None
            and not self._sealed
            and widget in top.changes
            and len(top.changes) == 1
            and time.monotonic() - top.time < MERGE_SECONDS
        ):
            top.record(widget, old, new)
            top.time = time.monotonic()
            if not top.changes:
                self._undo.pop()
        else:
            self._push(_Edit(widget, old, new))
        self._sealed = False
        self._redo.clear()
        self._update()

    def begin_group(self) -> None:
        """The changes until end_group are one step (several controls, one Undo)."""
        if self._group_depth == 0:
            self._group = None
            self._sealed = True
        self._group_depth += 1

    def end_group(self) -> None:
        if self._group_depth == 0:
            return
        self._group_depth -= 1
        if self._group_depth:
            return
        edit, self._group = self._group, None
        if edit is not None and edit.changes:
            self._push(edit)
            self._redo.clear()
            self._sealed = True
        self._update()

    def _push(self, edit: _Edit) -> None:
        self._undo.append(edit)
        while len(self._undo) > MAX_STEPS:
            self._undo.pop(0)

    def external_change(self, widget) -> None:
        """The JD-Xi sent another value: a step on it would restore what the instrument no longer has."""
        if self._replaying:
            return
        changed = False
        for stack in (self._undo, self._redo):
            for edit in list(stack):
                if edit.changes.pop(widget, None) is not None:
                    changed = True
                    if not edit.changes:
                        stack.remove(edit)
        if (
            self._group is not None
            and self._group.changes.pop(widget, None) is not None
        ):
            changed = True
        if self._origin.pop(widget, None) is not None:
            changed = True
        if changed:
            self._update()

    # -------------------------------------------------------------- undo / redo
    def can_undo(self) -> bool:
        return bool(self._undo)

    def can_redo(self) -> bool:
        return bool(self._redo)

    def can_restore(self) -> bool:
        """Something differs from the sound before the changes (Reload)."""
        return any(
            self._safe_shown(widget) != value for widget, value in self._origin.items()
        )

    def undo(self) -> bool:
        while self._group_depth:
            self.end_group()
        if not self._undo:
            return False
        edit = self._undo[-1]
        if not self._apply_all(
            [
                (widget, old)
                for widget, (old, _new) in reversed(list(edit.changes.items()))
            ]
        ):
            return False
        self._undo.pop()
        self._redo.append(edit)
        self._sealed = True
        self._update()
        return True

    def redo(self) -> bool:
        while self._group_depth:
            self.end_group()
        if not self._redo:
            return False
        edit = self._redo[-1]
        if not self._apply_all(
            [(widget, new) for widget, (_old, new) in edit.changes.items()]
        ):
            return False
        self._redo.pop()
        self._undo.append(edit)
        self._sealed = True
        self._update()
        return True

    def revert(self) -> bool:
        """Restore the values from before this editor's changes and clear the steps."""
        while self._group_depth:
            self.end_group()
        if not self._apply_all(list(self._origin.items())):
            return False
        self.reset()
        return True

    def reset(self) -> None:
        """A new sound: nothing to undo."""
        self._group_depth = 0
        self._group = None
        self._undo.clear()
        self._redo.clear()
        self._origin.clear()
        self._sealed = True
        self._update()

    def _apply_all(self, values: list) -> bool:
        done = []
        try:
            for widget, value in values:
                before = self._safe_shown(widget)
                if before != value:
                    self._apply(widget, value)
                    done.append((widget, before))
            return True
        except Exception as ex:
            for widget, before in reversed(done):
                try:
                    self._apply(widget, before)
                except Exception:
                    pass
            from decologr import Decologr as log

            log.error(scope="EditHistory", message=f"Undo / Redo not applied: {ex}")
            return False

    def _apply(self, widget, value: int) -> None:
        """Set the control as the user would, so the value is sent to the JD-Xi."""
        self._replaying = True
        try:
            widget.setValue(int(value))
        finally:
            self._replaying = False

    @staticmethod
    def _safe_shown(widget) -> Optional[int]:
        try:
            return shown_value(widget)
        except (TypeError, ValueError, RuntimeError):
            return None

    def _update(self) -> None:
        modified = self.can_restore()
        if modified != self._modified:
            self._modified = modified
            for callback in self._on_modified:
                callback(modified)
        for callback in self._on_state:
            callback()


def install_edit_history(editor: QWidget) -> EditHistory:
    """Undo, Redo and Reload at the top of a tone editor, recording its controls."""
    history = EditHistory(editor)
    editor.history = history

    mark = QLabel("Modified")
    mark.setObjectName("editModified")
    mark.setToolTip("This editor's values differ from the sound before the changes")
    mark.setVisible(False)
    history.on_modified(mark.setVisible)

    undo = QPushButton("Undo")
    redo = QPushButton("Redo")
    reload_button = QPushButton("Reload")
    undo.setObjectName("editUndo")
    redo.setObjectName("editRedo")
    reload_button.setObjectName("editReload")
    undo.setToolTip("Undo the last change")
    redo.setToolTip("Redo the last change taken back")
    reload_button.setToolTip(
        "Restore every value to what it was before the first change"
    )
    undo.clicked.connect(lambda: history.undo())
    redo.clicked.connect(lambda: history.redo())
    reload_button.clicked.connect(lambda: history.revert())

    def update() -> None:
        undo.setEnabled(history.can_undo())
        redo.setEnabled(history.can_redo())
        reload_button.setEnabled(history.can_restore())

    history.on_state(update)
    update()

    row = QHBoxLayout()
    row.addWidget(mark)
    row.addStretch()
    row.addWidget(undo)
    row.addWidget(redo)
    row.addWidget(reload_button)
    layout = editor.layout()
    if layout is not None:
        layout.insertLayout(0, row)
    return history
