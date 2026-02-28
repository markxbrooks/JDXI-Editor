"""
Pattern Widget Module

Manages a collection of PatternMeasureWidgets and their underlying PatternMeasure data models.
Acts as the main container for the pattern sequencer grid.
"""

from dataclasses import dataclass
from typing import Callable, List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.ui.editors.pattern.helper import (
    get_button_note_spec,
    set_sequencer_style,
)
from jdxi_editor.ui.editors.pattern.step.data import StepData
from jdxi_editor.ui.widgets.pattern.measure import PatternMeasure
from jdxi_editor.ui.widgets.pattern.measure_widget import PatternMeasureWidget
from jdxi_editor.ui.widgets.pattern.sequencer_button import SequencerButton


@dataclass
class PatternConfig:
    """Configuration for PatternWidget"""

    rows: int = 4
    steps_per_measure: int = 16
    initial_measures: int = 1


class PatternWidget(QWidget):
    """
    Main pattern widget containing multiple measures.

    Manages:
    - Collection of PatternMeasureWidget (UI) and PatternMeasure (data model)
    - Synchronization between UI and data model
    - Measure selection and navigation
    - Pattern-wide operations (copy, paste, clear, etc.)
    """

    def __init__(
        self,
        config: PatternConfig = None,
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize the PatternWidget.

        :param config: PatternConfig with dimensions and initial state
        :param parent: Parent QWidget
        """
        super().__init__(parent)
        self.config = config or PatternConfig()

        # UI Components
        self.measure_widgets: List[PatternMeasureWidget] = []
        self.measures_list: Optional[QListWidget] = None

        # Data Models
        self.measures: List[PatternMeasure] = []

        # State
        self.current_measure_index: int = 0
        self._clipboard: Optional[dict] = None

        # Callbacks
        self.on_measure_selected: Optional[Callable[[int], None]] = None
        self.on_measure_added: Optional[Callable[[int], None]] = None
        self.on_measure_removed: Optional[Callable[[int], None]] = None
        self._button_click_handler: Optional[
            Callable[[SequencerButton, bool], None]
        ] = None

        self._setup_ui()
        self._initialize_measures(self.config.initial_measures)
        self._show_current_measure()

    def _setup_ui(self) -> None:
        """Setup the UI layout."""
        main_layout = QHBoxLayout()

        # Measures list (navigation panel)
        self.measures_list = QListWidget()
        self.measures_list.setMaximumWidth(150)
        self.measures_list.itemSelectionChanged.connect(self._on_measure_selected)

        # Sequencer display area (header optional, content from _show_current_measure)
        self.sequencer_display = QVBoxLayout()
        self._sequencer_right = QWidget()
        self._sequencer_right_layout = QVBoxLayout(self._sequencer_right)
        self._sequencer_right_layout.addLayout(self.sequencer_display)

        main_layout.addWidget(self.measures_list, 1)  # Navigation
        main_layout.addWidget(self._sequencer_right, 4)  # Main display

        self.setLayout(main_layout)

    def set_header_widget(self, widget: QWidget) -> None:
        """Insert a header widget above the sequencer (e.g. row headers, presets)."""
        self._sequencer_right_layout.insertWidget(0, widget)

    def _initialize_measures(self, count: int) -> None:
        """Initialize pattern with specified number of measures."""
        for i in range(count):
            self._add_measure()

    def add_measure(self, copy_previous: bool = False) -> int:
        """
        Add a new measure to the pattern.

        :param copy_previous: If True, copy the previous measure's data
        :return: Index of the newly added measure
        """
        return self._add_measure(copy_previous)

    def _add_measure(self, copy_previous: bool = False) -> int:
        """Internal method to add a measure."""
        measure_index = len(self.measures)

        # Create data model
        measure = PatternMeasure(
            rows=self.config.rows, steps_per_bar=self.config.steps_per_measure
        )
        self.measures.append(measure)

        # Create UI widget and apply sequencer styling
        widget = PatternMeasureWidget()
        self._apply_sequencer_style(widget)
        self._wire_button_clicks(widget)

        # Copy from previous if requested
        if copy_previous and measure_index > 0:
            self._copy_measure_data(
                self.measures[measure_index - 1],
                measure,
                self.measure_widgets[measure_index - 1],
                widget,
            )

        self.measure_widgets.append(widget)

        # Add to list widget
        self._add_to_measures_list(measure_index)

        if self.on_measure_added:
            self.on_measure_added(measure_index)

        return measure_index

    def remove_measure(self, index: int) -> bool:
        """
        Remove a measure at the specified index.

        :param index: Measure index
        :return: True if successful, False otherwise
        """
        if index < 0 or index >= len(self.measures):
            return False

        self.measures.pop(index)
        self.measure_widgets.pop(index)

        # Update list widget
        item = self.measures_list.item(index)
        if item:
            self.measures_list.takeItem(index)

        # Update current selection
        if self.current_measure_index >= len(self.measures):
            self.current_measure_index = max(0, len(self.measures) - 1)

        if self.on_measure_removed:
            self.on_measure_removed(index)

        return True

    def select_measure(self, index: int) -> bool:
        """
        Select a measure by index.

        :param index: Measure index (0-based)
        :return: True if successful
        """
        if index < 0 or index >= len(self.measures):
            return False

        self.current_measure_index = index
        if self.measures_list:
            self.measures_list.setCurrentRow(index)

        self._show_current_measure()

        if self.on_measure_selected:
            self.on_measure_selected(index)

        return True

    def get_current_measure(self) -> Optional[PatternMeasure]:
        """Get the current selected measure data model."""
        if 0 <= self.current_measure_index < len(self.measures):
            return self.measures[self.current_measure_index]
        return None

    def get_current_measure_widget(self) -> Optional[PatternMeasureWidget]:
        """Get the current selected measure widget."""
        if 0 <= self.current_measure_index < len(self.measure_widgets):
            return self.measure_widgets[self.current_measure_index]
        return None

    def sync_ui_to_measure(self, measure_index: int) -> None:
        """
        Synchronize UI buttons with measure data.

        :param measure_index: Index of measure to sync to
        """
        if measure_index < 0 or measure_index >= len(self.measures):
            return

        measure = self.measures[measure_index]
        widget = self.measure_widgets[measure_index]

        for row in range(self.config.rows):
            for step in range(self.config.steps_per_measure):
                if step >= len(measure.steps[row]):
                    continue

                step_data = measure.steps[row][step]
                button = widget.buttons[row][step]

                button.setChecked(step_data.active)
                button.note = step_data.note
                button.note_velocity = step_data.velocity
                button.note_duration = step_data.duration_steps

    def sync_measure_to_ui(self, measure_index: int) -> None:
        """
        Synchronize measure data with UI button state.

        :param measure_index: Index of measure to sync from
        """
        if measure_index < 0 or measure_index >= len(self.measures):
            return

        measure = self.measures[measure_index]
        widget = self.measure_widgets[measure_index]

        for row in range(self.config.rows):
            for step in range(self.config.steps_per_measure):
                if step >= len(measure.steps[row]):
                    continue

                button = widget.buttons[row][step]
                step_data = measure.steps[row][step]

                step_data.active = button.isChecked()
                step_data.note = button.note or 60
                step_data.velocity = button.note_velocity or 100
                step_data.duration_steps = button.note_duration

    def copy_measure(self, from_index: int, to_index: int) -> bool:
        """
        Copy measure data from one index to another.

        :param from_index: Source measure index
        :param to_index: Destination measure index
        :return: True if successful
        """
        if from_index < 0 or from_index >= len(self.measures):
            return False
        if to_index < 0 or to_index >= len(self.measures):
            return False

        self._copy_measure_data(
            self.measures[from_index],
            self.measures[to_index],
            self.measure_widgets[from_index],
            self.measure_widgets[to_index],
        )

        return True

    def copy_measure_section(
        self, measure_index: int, start_step: int, end_step: int
    ) -> Optional[dict]:
        """
        Copy a section of steps from a measure. Reads from buttons (source of truth).

        Returns clipboard dict compatible with ClipboardData format: start_step, end_step,
        source_bar, notes_data. Also includes "rows" for backward compatibility.
        """
        if measure_index < 0 or measure_index >= len(self.measure_widgets):
            return None

        widget = self.measure_widgets[measure_index]

        section_data: dict = {
            "start_step": start_step,
            "end_step": end_step,
            "source_bar": measure_index,
            "rows": {},
            "notes_data": {},
        }

        for row in range(self.config.rows):
            if row >= len(widget.buttons):
                continue
            section_data["rows"][row] = {}
            section_data["notes_data"][row] = {}
            for step in range(start_step, end_step + 1):
                if step >= len(widget.buttons[row]):
                    continue
                button = widget.buttons[row][step]
                spec = get_button_note_spec(button)
                step_dict = {
                    "checked": button.isChecked(),
                    "active": button.isChecked(),
                    "note": spec.note,
                    "velocity": spec.velocity if spec.is_active else 100,
                    "duration_ms": spec.duration_ms if spec.is_active else None,
                }
                section_data["rows"][row][step] = step_dict
                section_data["notes_data"][row][step] = {
                    "checked": step_dict["checked"],
                    "note": step_dict["note"],
                    "duration": step_dict["duration_ms"],
                    "velocity": step_dict["velocity"],
                }

        self._clipboard = section_data
        return section_data

    def paste_measure_section(
        self, measure_index: int, start_step: int, clipboard: Optional[dict] = None
    ) -> bool:
        """
        Paste a section of steps into a measure. Accepts ClipboardData format
        (notes_data) or PatternWidget format (rows). Handles checked/active,
        duration/duration_ms for cross-component compatibility.
        """
        if measure_index < 0 or measure_index >= len(self.measure_widgets):
            return False

        clip = clipboard or self._clipboard
        if not clip:
            return False

        # Support both ClipboardData ("notes_data") and PatternWidget ("rows") format
        rows_data = clip.get("notes_data") or clip.get("rows")
        if not rows_data:
            return False

        source_start = clip["start_step"]
        source_end = clip["end_step"]
        measure = self.measures[measure_index]
        widget = self.measure_widgets[measure_index]

        for row in range(self.config.rows):
            if row not in rows_data:
                continue
            for source_step, step_data_dict in rows_data[row].items():
                dest_step = start_step + (source_step - source_start)
                if dest_step < 0 or dest_step >= self.config.steps_per_measure:
                    continue
                if dest_step >= len(widget.buttons[row]):
                    continue

                button = widget.buttons[row][dest_step]
                checked = step_data_dict.get(
                    "checked", step_data_dict.get("active", False)
                )
                note = step_data_dict.get("note")
                velocity = step_data_dict.get("velocity", 100)
                duration_ms = step_data_dict.get("duration_ms") or step_data_dict.get(
                    "duration"
                )

                button.setChecked(checked)
                button.note = note
                button.note_velocity = velocity
                button.note_duration = duration_ms

                # Sync to PatternMeasure for consistency
                step_data = measure.steps[row][dest_step]
                step_data.active = checked
                step_data.note = note or 60
                step_data.velocity = velocity
                step_data.duration_steps = 1 if duration_ms else 0

        return True

    def clear_measure(self, measure_index: int) -> bool:
        """
        Clear all steps in a measure.

        :param measure_index: Measure index
        :return: True if successful
        """
        if measure_index < 0 or measure_index >= len(self.measures):
            return False

        measure = self.measures[measure_index]
        widget = self.measure_widgets[measure_index]

        for row in range(self.config.rows):
            for step in range(self.config.steps_per_measure):
                step_data = measure.steps[row][step]
                step_data.active = False
                step_data.note = 60
                step_data.velocity = 100
                step_data.duration_steps = 1

                button = widget.buttons[row][step]
                button.setChecked(False)
                button.note = None
                button.note_velocity = None
                button.note_duration = None

        return True

    def clear_all_measures(self) -> None:
        """Clear all measures in the pattern."""
        for i in range(len(self.measures)):
            self.clear_measure(i)

    def get_measure_count(self) -> int:
        """Get total number of measures."""
        return len(self.measures)

    def get_measure_widgets(self) -> List[PatternMeasureWidget]:
        """Return all measure widgets (for playback, save, etc.)."""
        return self.measure_widgets

    def ensure_measure_count(self, count: int) -> None:
        """Add or remove measures to match count."""
        current = len(self.measures)
        if count > current:
            for _ in range(count - current):
                self.add_measure(copy_previous=False)
        elif count < current:
            for _ in range(current - count):
                self.remove_measure(len(self.measures) - 1)

    def clear_and_reset(self, initial_count: int = 1) -> None:
        """Clear all measures and list; optionally add initial_count empty measures."""
        self.measures.clear()
        self.measure_widgets.clear()
        if self.measures_list:
            self.measures_list.clear()
        self.current_measure_index = 0
        for _ in range(initial_count):
            self._add_measure()
        self._show_current_measure()

    def _show_current_measure(self) -> None:
        """Remove previous content and show current measure widget in sequencer_display."""
        while self.sequencer_display.count():
            item = self.sequencer_display.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        if 0 <= self.current_measure_index < len(self.measure_widgets):
            w = self.measure_widgets[self.current_measure_index]
            self.sequencer_display.addWidget(w)

    def _apply_sequencer_style(self, widget: PatternMeasureWidget) -> None:
        """Apply sequencer button styling to all buttons in the measure widget."""
        for row in widget.buttons:
            for btn in row:
                set_sequencer_style(btn, is_current=False, checked=btn.isChecked())

    def _wire_button_clicks(self, widget: PatternMeasureWidget) -> None:
        """Wire button clicks to handler if set."""
        if not self._button_click_handler:
            return
        for row in widget.buttons:
            for btn in row:
                btn.clicked.connect(
                    lambda checked, b=btn: self._button_click_handler(b, checked)  # type: ignore[misc]
                )

    def set_button_click_handler(
        self, handler: Optional[Callable[[SequencerButton, bool], None]]
    ) -> None:
        """Set handler for button clicks; wires all current and future measure widgets."""
        self._button_click_handler = handler
        for mw in self.measure_widgets:
            self._wire_button_clicks(mw)

    def get_total_steps(self) -> int:
        """Get total number of steps across all measures."""
        return self.get_measure_count() * self.config.steps_per_measure

    def _copy_measure_data(
        self,
        source_measure: PatternMeasure,
        dest_measure: PatternMeasure,
        source_widget: PatternMeasureWidget,
        dest_widget: PatternMeasureWidget,
    ) -> None:
        """Internal helper to copy measure data and UI state."""
        for row in range(self.config.rows):
            for step in range(self.config.steps_per_measure):
                source_data = source_measure.steps[row][step]
                dest_data = dest_measure.steps[row][step]

                # Copy data model
                dest_data.active = source_data.active
                dest_data.note = source_data.note
                dest_data.velocity = source_data.velocity
                dest_data.duration_steps = source_data.duration_steps

                # Copy UI state
                source_button = source_widget.buttons[row][step]
                dest_button = dest_widget.buttons[row][step]

                dest_button.setChecked(source_button.isChecked())
                dest_button.note = source_button.note
                dest_button.note_velocity = source_button.note_velocity
                dest_button.note_duration = source_button.note_duration

    def _add_to_measures_list(self, measure_index: int) -> QListWidgetItem:
        """Add measure to the list widget."""
        item = QListWidgetItem(f"Measure {measure_index + 1}")
        item.setData(Qt.ItemDataRole.UserRole, measure_index)
        self.measures_list.addItem(item)
        return item

    def _on_measure_selected(self) -> None:
        """Handle measure selection from list widget."""
        row = self.measures_list.currentRow()
        if 0 <= row < len(self.measures):
            self.select_measure(row)

    def scroll_to_measure(self, measure_index: int) -> None:
        """Scroll measures list to show the specified measure."""
        if self.measures_list and 0 <= measure_index < self.measures_list.count():
            item = self.measures_list.item(measure_index)
            if item:
                self.measures_list.scrollToItem(item)
