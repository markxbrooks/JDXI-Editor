"""
Pattern Widget Module

Manages a collection of PatternMeasureWidgets and their underlying PatternMeasure data models.
Acts as the main container for the pattern sequencer grid.
"""

from typing import List, Optional, Callable
from dataclasses import dataclass

from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QHBoxLayout
from PySide6.QtCore import Qt

from jdxi_editor.ui.widgets.pattern.measure_widget import PatternMeasureWidget
from jdxi_editor.ui.widgets.pattern.measure import PatternMeasure
from jdxi_editor.ui.widgets.pattern.sequencer_button import SequencerButton
from jdxi_editor.ui.editors.pattern.step.data import StepData


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

        self._setup_ui()
        self._initialize_measures(self.config.initial_measures)

    def _setup_ui(self) -> None:
        """Setup the UI layout."""
        main_layout = QHBoxLayout()

        # Measures list (navigation panel)
        self.measures_list = QListWidget()
        self.measures_list.itemSelectionChanged.connect(self._on_measure_selected)

        # Sequencer display area
        self.sequencer_display = QVBoxLayout()

        main_layout.addWidget(self.measures_list, 1)  # Navigation
        main_layout.addLayout(self.sequencer_display, 4)  # Main display

        self.setLayout(main_layout)

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
            rows=self.config.rows,
            steps_per_bar=self.config.steps_per_measure
        )
        self.measures.append(measure)

        # Create UI widget
        widget = PatternMeasureWidget()

        # Copy from previous if requested
        if copy_previous and measure_index > 0:
            self._copy_measure_data(
                self.measures[measure_index - 1],
                measure,
                self.measure_widgets[measure_index - 1],
                widget
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
            self.measure_widgets[to_index]
        )

        return True

    def copy_measure_section(
            self,
            measure_index: int,
            start_step: int,
            end_step: int
    ) -> Optional[dict]:
        """
        Copy a section of steps from a measure.

        :param measure_index: Measure index
        :param start_step: Start step (inclusive)
        :param end_step: End step (inclusive)
        :return: Dictionary with copied data, or None if failed
        """
        if measure_index < 0 or measure_index >= len(self.measures):
            return None

        measure = self.measures[measure_index]
        widget = self.measure_widgets[measure_index]

        section_data = {
            "start_step": start_step,
            "end_step": end_step,
            "rows": {}
        }

        for row in range(self.config.rows):
            section_data["rows"][row] = {}
            for step in range(start_step, end_step + 1):
                if step >= len(measure.steps[row]):
                    continue

                button = widget.buttons[row][step]
                step_data = measure.steps[row][step]

                section_data["rows"][row][step] = {
                    "active": step_data.active,
                    "note": step_data.note,
                    "velocity": step_data.velocity,
                    "duration": step_data.duration_steps,
                }

        self._clipboard = section_data
        return section_data

    def paste_measure_section(
            self,
            measure_index: int,
            start_step: int,
            clipboard: Optional[dict] = None
    ) -> bool:
        """
        Paste a section of steps into a measure.

        :param measure_index: Destination measure index
        :param start_step: Starting step for paste
        :param clipboard: Clipboard data (uses self._clipboard if None)
        :return: True if successful
        """
        if measure_index < 0 or measure_index >= len(self.measures):
            return False

        clip = clipboard or self._clipboard
        if not clip:
            return False

        measure = self.measures[measure_index]
        widget = self.measure_widgets[measure_index]

        source_start = clip["start_step"]
        source_end = clip["end_step"]
        num_steps = source_end - source_start + 1

        for row in range(self.config.rows):
            if row not in clip["rows"]:
                continue

            for source_step, step_data_dict in clip["rows"][row].items():
                dest_step = start_step + (source_step - source_start)

                if dest_step < 0 or dest_step >= self.config.steps_per_measure:
                    continue

                button = widget.buttons[row][dest_step]
                step_data = measure.steps[row][dest_step]

                step_data.active = step_data_dict["active"]
                step_data.note = step_data_dict["note"]
                step_data.velocity = step_data_dict["velocity"]
                step_data.duration_steps = step_data_dict["duration"]

                button.setChecked(step_data.active)
                button.note = step_data.note
                button.note_velocity = step_data.velocity
                button.note_duration = step_data.duration_steps

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

    def get_total_steps(self) -> int:
        """Get total number of steps across all measures."""
        return self.get_measure_count() * self.config.steps_per_measure

    def _copy_measure_data(
            self,
            source_measure: PatternMeasure,
            dest_measure: PatternMeasure,
            source_widget: PatternMeasureWidget,
            dest_widget: PatternMeasureWidget
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
        current_item = self.measures_list.currentItem()
        if current_item:
            measure_index = current_item.data(Qt.ItemDataRole.UserRole)
            if measure_index is not None:
                self.select_measure(measure_index)

    def scroll_to_measure(self, measure_index: int) -> None:
        """Scroll measures list to show the specified measure."""
        if self.measures_list and 0 <= measure_index < self.measures_list.count():
            item = self.measures_list.item(measure_index)
            if item:
                self.measures_list.scrollToItem(item)