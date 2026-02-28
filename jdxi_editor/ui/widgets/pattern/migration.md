# Migration Plan: Extracting PatternWidget from PatternSequenceEditor

## Executive Summary

This document maps the measure-related architecture in `PatternSequenceEditor`/`PatternUI`, compares it with `PatternWidget`, identifies gaps, and provides a concrete migration plan with file paths and code changes.

---

## 1. PatternSequenceEditor / PatternUI Measure Mapping

### 1.1 Architecture Overview

**PatternSequenceEditor** uses a **split storage vs. display** model:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  PatternSequenceEditor (extends PatternUI)                                │
│                                                                          │
│  ┌──────────────────────┐    ┌─────────────────────────────────────────┐ │
│  │ measures_list        │    │ _create_sequencer_widget()              │ │
│  │ (QListWidget)        │    │ → ONE fixed 4×16 grid: self.buttons     │ │
│  │ - Measure 1          │    │   (the visible, editable grid)          │ │
│  │ - Measure 2          │    │                                         │ │
│  │ - ...                │    │   User edits HERE; data stored in       │ │
│  └──────────────────────┘    │   measure_widgets[current_measure_index]│ │
│           │                  └─────────────────────────────────────────┘ │
│           │                                        │                      │
│           │                    _sync_sequencer_with_measure()             │
│           │                    _store_note_in_measures()                 │
│           ▼                                        │                      │
│  ┌──────────────────────┐                          ▼                      │
│  │ measure_widgets[]    │  ◄── Storage: one PatternMeasureWidget per    │
│  │ (PatternMeasureWidget)│     measure. Each has 4×16 SequencerButtons.  │
│  │ - buttons[4][16]     │     NOT displayed; used as data store.         │
│  └──────────────────────┘                                                │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key insight:** The visible sequencer is `self.buttons` (4×16). Each measure's data lives in `measure_widgets[i].buttons`. On measure select: sync `measure_widgets[i]` → `buttons`. On button click: sync `buttons` → `measure_widgets[current_measure_index]`.

### 1.2 Measure-Related Attributes (PatternUI / PatternSequenceEditor)

| Attribute | Type | Location | Purpose |
|-----------|------|----------|---------|
| `measure_widgets` | `list[PatternMeasureWidget]` | ui.py:130, pattern.py | One per measure; each has `.buttons[row][step]` (SequencerButton) |
| `measures` | `list[PatternMeasure]` | ui.py:134 | **Unused/dead** – never populated; only referenced in `on_button_toggled`/`sync_ui_to_measure` (would IndexError if called) |
| `measures_list` | `QListWidget` | ui.py:425 | Navigation; items store index in UserRole |
| `buttons` | `list[list[SequencerButton]]` | ui.py:211, 458 | Single 4×16 visible grid (shared display) |
| `current_measure_index` | `int` | ui.py:135 | Index of selected measure |
| `total_measures` | `int` | ui.py:118, pattern.py | Count of measures |
| `measure_beats` | `int` | ui.py:130 | 16 or 12 steps per measure |
| `clipboard` | `dict` | ui.py:140 | Copy/paste: source_bar, start_step, end_step, notes_data |

### 1.3 Measure-Related Methods

#### PatternUI (ui.py)

| Method | Lines | Purpose |
|--------|-------|---------|
| `_create_measures_group()` | 421–430 | Creates `measures_list` QListWidget in QGroupBox |
| `_on_measure_selected(item)` | 371–372 | **NotImplementedError** – subclass implements |
| `_build_splitter_section()` | 263–274 | Splitter: measures group + sequencer widget |
| `_create_sequencer_widget()` | 275–286 | Builds 4 rows via `_create_sequencer_row()` → `ui_generate_button_row()` |
| `ui_generate_button_row()` | 454–466 | Creates one row of SequencerButtons → `self.buttons[row]` |

#### PatternSequenceEditor (pattern.py)

| Method | Lines | Purpose |
|--------|-------|---------|
| `_on_measure_selected(item)` | 784–793 | Set `current_measure_index`, call `_sync_sequencer_with_measure()` |
| `_add_measure()` | 496–538 | Add PatternMeasureWidget; optionally copy from previous; update list and sync |
| `_add_to_measures_list()` | 550–558 | Add item "Measure N" with UserRole=index |
| `_sync_sequencer_with_measure(bar_index)` | 893–916 | Copy `measure_widgets[bar_index].buttons` → `self.buttons` |
| `_store_note_in_measures(button, checked)` | 1036–1054 | Copy `self.buttons` state → `measure_widgets[current].buttons` |
| `_on_button_clicked(button, checked)` | 998–1034 | Handle note selection; call `_store_note_in_measures` |
| `_copy_section()` | 796–826 | Copy steps to `clipboard` (notes_data from measure_widget) |
| `_paste_section()` | 827–854 | Paste from clipboard to current measure_widget |
| `_scroll_measures_list_to(measure_index)` | 451–457 | Select and scroll list to index |
| `_on_measure_count_changed(count)` | 971–988 | Add/remove measures to match count |
| `_update_pattern_length()` | 990–994 | Update `total_steps` (keeps 16) |
| `reset_all_measures()` | 740–744 | Reset all measure_widgets |
| `add_and_reset_new_measure()` | 746–751 | Create empty PatternMeasureWidget, append |
| `_clear_measures_and_measures_list()` | 1623–1626 | Clear list and measure_widgets |
| `_create_new_measures(num_bars)` | 1521–1530 | Create num_bars empty PatternMeasureWidgets |
| `clear_pattern()` | 1714–1725 | Clear current measure's buttons |
| `on_button_toggled()` | 204–207 | **Uses `self.measures`** – likely dead (measures never populated) |
| `sync_ui_to_measure(bar_index)` | 210–222 | **Uses `self.measures`** – same |

### 1.4 Data Flow Summary

- **Display:** `self.buttons` (4×16) – built by PatternUI, shown in sequencer area.
- **Storage:** `self.measure_widgets[i]` – each `PatternMeasureWidget` has `.buttons[row][step]`.
- **Select measure:** `_sync_sequencer_with_measure(index)` copies measure_widget → buttons.
- **Edit:** `_store_note_in_measures()` copies buttons → current measure_widget.
- **Playback/Save:** Iterate `measure_widgets`, use `get_button_note_spec(button)` for note data.

---

## 2. PatternWidget Current API

### 2.1 Architecture

**PatternWidget** uses **dual model (data + UI)** and does **not** populate the sequencer display:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  PatternWidget (jdxi_editor/ui/widgets/pattern/widget.py)                 │
│                                                                          │
│  ┌──────────────────────┐    ┌─────────────────────────────────────────┐ │
│  │ measures_list        │    │ sequencer_display (QVBoxLayout)          │ │
│  │ (QListWidget)        │    │                                         │ │
│  │ - Measure 1          │    │   EMPTY – never populated with           │ │
│  │ - Measure 2          │    │   measure_widgets!                       │ │
│  └──────────────────────┘    └─────────────────────────────────────────┘ │
│                                                                          │
│  measures: list[PatternMeasure]     ← StepData (active, note, velocity)   │
│  measure_widgets: list[PatternMeasureWidget]  ← Created but not shown     │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Attributes

| Attribute | Type | Purpose |
|-----------|------|---------|
| `config` | `PatternConfig` | `rows`, `steps_per_measure`, `initial_measures` |
| `measure_widgets` | `list[PatternMeasureWidget]` | UI for each measure (created but not added to layout) |
| `measures` | `list[PatternMeasure]` | Data model with `steps[row][step]` (StepData) |
| `measures_list` | `QListWidget` | Navigation |
| `sequencer_display` | `QVBoxLayout` | **Empty** – no widgets added |
| `current_measure_index` | `int` | Selected measure |
| `_clipboard` | `dict` | Section copy/paste |
| `on_measure_selected` | `Callable[[int], None]` | Callback |
| `on_measure_added` | `Callable[[int], None]` | Callback |
| `on_measure_removed` | `Callable[[int], None]` | Callback |

### 2.3 Methods

| Method | Purpose |
|--------|---------|
| `add_measure(copy_previous=False)` | Add PatternMeasure + PatternMeasureWidget; copy if requested |
| `remove_measure(index)` | Remove measure and widget |
| `select_measure(index)` | Set selection, update list |
| `get_current_measure()` | Return current `PatternMeasure` |
| `get_current_measure_widget()` | Return current `PatternMeasureWidget` |
| `sync_ui_to_measure(measure_index)` | Copy `measure.steps` → widget buttons |
| `sync_measure_to_ui(measure_index)` | Copy widget buttons → `measure.steps` |
| `copy_measure(from_index, to_index)` | Copy one measure to another |
| `copy_measure_section(measure_index, start_step, end_step)` | Copy section to clipboard |
| `paste_measure_section(...)` | Paste from clipboard |
| `clear_measure(measure_index)` | Reset all steps |
| `clear_all_measures()` | Clear all |
| `get_measure_count()` | `len(measures)` |
| `get_total_steps()` | `measure_count * steps_per_measure` |
| `scroll_to_measure(index)` | Scroll list to item |

### 2.4 Data Model: PatternMeasure vs. PatternMeasureWidget

- **PatternMeasure:** `steps[row][step]` = `StepData(active, note, velocity, duration_steps)`.
- **PatternMeasureWidget:** `buttons[row][step]` = `SequencerButton` with `.note`, `.note_velocity`, `.note_duration`, `.isChecked()`.

PatternWidget syncs between these via `sync_ui_to_measure` / `sync_measure_to_ui`. PatternSequenceEditor uses only `PatternMeasureWidget` (no `PatternMeasure` / `StepData`).

---

## 3. Gap Analysis: What PatternWidget Needs

### 3.1 Critical Gaps

| Gap | Detail | Required Change |
|-----|--------|-----------------|
| **1. Sequencer display empty** | `sequencer_display` has no widgets | Add current measure's widget to layout, or implement single-grid display mode |
| **2. Single vs. multi measure display** | PatternSequenceEditor shows **one** 4×16 grid at a time | PatternWidget must support "single measure display" – one visible grid synced with selected measure |
| **3. Row headers / presets** | PatternUI has row labels, icons, combo selectors (digital1, digital2, analog, drum) | PatternWidget has none | Either add row header support or keep them in PatternSequenceEditor and wire to widget |
| **4. Mute buttons** | PatternUI has per-row mute | PatternWidget has none | Add or delegate to parent |
| **5. Button click handling** | PatternSequenceEditor: `_on_button_clicked` → note from combo, velocity, duration | PatternWidget: buttons exist but no combo/duration/velocity wiring | PatternWidget needs configurable note source (combo, callback) and velocity/duration |
| **6. Styling** | PatternSequenceEditor uses `generate_sequencer_button_style`, `set_sequencer_style` | PatternMeasureWidget creates plain SequencerButtons | Apply same styling in PatternWidget |
| **7. Clipboard format** | PatternSequenceEditor: `ClipboardData` (notes_data with `NoteButtonSpec`-like structure) | PatternWidget: `copy_measure_section` uses `duration` key | Align format for interoperability |
| **8. Beats per measure** | PatternUI: 16 or 12 (3/4 time) | PatternWidget: fixed `steps_per_measure` in config | Add config option and button enable/disable for 12-beat mode |

### 3.2 Integration Points

| Integration | PatternSequenceEditor needs from PatternWidget |
|-------------|-----------------------------------------------|
| **Current measure data** | `get_current_measure_widget()` or equivalent for playback/save |
| **All measures** | `measure_widgets` or `get_measures_for_playback()` |
| **Measure count** | `get_measure_count()`, `total_measures` |
| **Sync on select** | Widget handles internal display sync; editor may need `on_measure_selected` callback |
| **Add/remove measures** | `add_measure()`, `remove_measure()` or delegate |

---

## 4. Integration: Delegates, Callbacks, Signals

### 4.1 Callbacks PatternWidget Should Support

```python
# Already in PatternWidget:
on_measure_selected: Callable[[int], None]
on_measure_added: Callable[[int], None]
on_measure_removed: Callable[[int], None]
```

### 4.2 Additional Callbacks Needed

```python
# For PatternSequenceEditor integration:
on_button_clicked: Callable[[SequencerButton, bool], None]  # Before/after toggle
on_step_changed: Callable[[int], None]  # Playback highlight (optional)
```

### 4.3 Data Access PatternSequenceEditor Needs

```python
# PatternWidget must provide:
def get_measure_widgets(self) -> list[PatternMeasureWidget]: ...
def get_current_measure_index(self) -> int: ...
def get_buttons_for_playback(self) -> list[list[SequencerButton]]:
    """For playback: iterate measure_widgets[current] or equivalent."""
```

Playback and save currently use `measure_widgets` and `get_button_note_spec(button)`. PatternWidget can expose `measure_widgets` or a wrapper that returns the same structure.

### 4.4 Configuration Injection

```python
@dataclass
class PatternConfig:
    rows: int = 4
    steps_per_measure: int = 16
    initial_measures: int = 1
    # New:
    beats_per_measure_options: tuple[int, ...] = (16, 12)  # Optional
    show_row_headers: bool = False  # If True, parent supplies headers
```

---

## 5. Concrete Migration Plan

### Phase 1: Extend PatternWidget (jdxi_editor/ui/widgets/pattern/widget.py)

#### 1.1 Add Single-Measure Display Mode

**Change:** Populate `sequencer_display` with the **current** measure's widget. Swap on selection.

```python
def _show_current_measure(self) -> None:
    """Remove previous, add current measure widget to sequencer_display."""
    # Clear existing
    while self.sequencer_display.count():
        item = self.sequencer_display.takeAt(0)
        if item.widget():
            item.widget().setParent(None)
    # Add current
    if 0 <= self.current_measure_index < len(self.measure_widgets):
        w = self.measure_widgets[self.current_measure_index]
        self.sequencer_display.addWidget(w)
```

Call `_show_current_measure()` from `select_measure()` and `_on_measure_selected()`.

**Alternative:** Keep PatternSequenceEditor’s architecture: one shared 4×16 grid, PatternWidget only manages `measure_widgets` and `measures_list`. Then `sequencer_display` would hold a **single** PatternMeasureWidget that is synced from the selected measure (display-only, edits go back to storage). This matches current behavior more closely.

#### 1.2 Wire Button Clicks (Optional Delegation)

```python
def set_button_click_handler(self, handler: Callable[[SequencerButton, bool], None]) -> None:
    """Set external handler for button clicks."""
    self._button_click_handler = handler
    for mw in self.measure_widgets:
        for row in mw.buttons:
            for btn in row:
                btn.clicked.disconnect()  # Remove default if any
                btn.clicked.connect(lambda checked, b=btn: handler(b, checked))
```

If using a single display grid (like PatternSequenceEditor), the parent would own the grid and handle clicks; PatternWidget would just sync data.

#### 1.3 Expose Measure Widgets for Playback

```python
def get_measure_widgets(self) -> list[PatternMeasureWidget]:
    return self.measure_widgets
```

#### 1.4 Apply Sequencer Styling

In `_add_measure()`, when creating `PatternMeasureWidget`, apply:

```python
from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.editors.pattern.helper import set_sequencer_style

# In PatternMeasureWidget or PatternWidget after creating buttons:
for row in widget.buttons:
    for btn in row:
        set_sequencer_style(btn)
```

---

### Phase 2: Refactor PatternUI / PatternSequenceEditor

#### 2.1 Introduce PatternWidget in PatternUI

**File:** `jdxi_editor/ui/editors/pattern/ui.py`

**Change:** Replace custom measures + sequencer layout with PatternWidget.

```python
# In PatternUI.__init__ or _setup_ui:
from jdxi_editor.ui.widgets.pattern.widget import PatternWidget, PatternConfig

self.pattern_widget = PatternWidget(config=PatternConfig(
    rows=4,
    steps_per_measure=self.measure_beats,  # 16 or 12
    initial_measures=1,
))
self.pattern_widget.on_measure_selected = self._on_pattern_measure_selected
self.pattern_widget.on_measure_added = self._on_pattern_measure_added

# In _build_splitter_section:
splitter.addWidget(self._create_measures_group())  # Can simplify to just pattern_widget.measures_list
splitter.addWidget(self.pattern_widget)  # Or add pattern_widget's sequencer portion
```

**Design choice:** Either:

- **Option A:** PatternWidget owns measures list + sequencer. PatternUI puts `pattern_widget` in the splitter (replace both measures group and sequencer widget).
- **Option B:** PatternUI keeps its own row headers/presets/mute, and PatternWidget only supplies the 4×16 grid (or measure storage). PatternWidget becomes the "measure data + list" component; the main grid stays in PatternUI.

Recommendation: **Option A** – PatternWidget owns measures list and sequencer. Row headers, presets, and mute stay in PatternUI and are laid out above or beside the PatternWidget.

#### 2.2 Remove Duplicate Measure Logic from PatternSequenceEditor

**File:** `jdxi_editor/ui/editors/pattern/pattern.py`

| Remove/Replace | With |
|----------------|------|
| `_add_measure()` | `self.pattern_widget.add_measure(copy_previous=...)` |
| `_on_measure_selected(item)` | `self.pattern_widget.select_measure(index)` + callback to `_sync_sequencer_with_measure` (if using shared grid) |
| `_sync_sequencer_with_measure(bar_index)` | Delegate to PatternWidget, or sync PatternWidget’s current measure widget to `self.buttons` if keeping shared grid |
| `_store_note_in_measures()` | Delegate to PatternWidget or have PatternWidget own the grid and do this internally |
| `measure_widgets` | `self.pattern_widget.get_measure_widgets()` or `self.pattern_widget.measure_widgets` |
| `measures_list` | `self.pattern_widget.measures_list` |
| `current_measure_index` | `self.pattern_widget.current_measure_index` |
| `total_measures` | `self.pattern_widget.get_measure_count()` |
| `_copy_section()`, `_paste_section()` | Call `pattern_widget.copy_measure_section`, `paste_measure_section` with editor’s spinbox values |
| `_clear_measures_and_measures_list()` | `pattern_widget.clear_all_measures()` + clear list, or add `clear_and_reset()` to PatternWidget |
| `_create_new_measures(num_bars)` | Loop `pattern_widget.add_measure()` or add `ensure_measure_count(count)` to PatternWidget |

#### 2.3 Handle Layout Differences

PatternUI’s sequencer includes row headers (icons, labels, combo boxes). Two approaches:

1. **PatternWidget embeds row headers:** Add optional `row_header_widgets` to PatternConfig; PatternUI supplies them and PatternWidget places them.
2. **PatternUI keeps headers:** PatternUI builds rows as `[header | PatternWidget row]`. PatternWidget would need to expose rows of buttons for this.

Simpler: have PatternWidget render the full sequencer (including headers) via a configurable row factory, or keep headers in PatternUI and have PatternWidget provide a widget that is just the 4×16 grid (or the current measure’s grid).

---

### Phase 3: Data Model Alignment ✅ DONE

#### 3.1 PatternMeasure vs. Button-Only Storage

PatternSequenceEditor uses **buttons only** (no `PatternMeasure`). PatternWidget uses **both** `PatternMeasure` and `PatternMeasureWidget`.

**Options:**

- **A)** PatternWidget drops `PatternMeasure` and uses only `PatternMeasureWidget` (like PatternSequenceEditor). Simpler but loses a separate data layer.
- **B)** Keep `PatternMeasure` and ensure `sync_measure_to_ui` / `sync_ui_to_measure` are called at the right times so playback/save can use either `measures` or `measure_widgets`. Current playback uses `get_button_note_spec(measure_button)`, so `measure_widgets` is sufficient.
- **C)** Add a `data_source` config: `"buttons"` (current behavior) vs. `"pattern_measure"`. Migration starts with `"buttons"` to match PatternSequenceEditor.

Recommendation: **B** – keep `PatternMeasure` for potential future use (export, undo, etc.) but ensure `measure_widgets` stay the source of truth for playback and save. PatternWidget can optionally sync to `measures` when needed.

#### 3.2 Clipboard Format

Unify on a single format. PatternWidget’s `copy_measure_section` returns:

```python
{"start_step": int, "end_step": int, "rows": {row: {step: {active, note, velocity, duration}}}}
```

PatternSequenceEditor uses `ClipboardData` with `notes_data` keyed by row/step. Align keys and structure so both can paste from each other.

---

### Phase 4: Cleanup (Post-Migration) ✅ DONE

**Removed dead code:**
- `_create_sequencer_widget`, `_create_measures_group` (replaced by PatternWidget)
- `_create_sequencer_row`, `_create_row_buttons`, `ui_generate_button_row` (unused)
- `_copy_rows_and_selected_steps`, `_paste_rows_and_selected_steps` (delegated to PatternWidget)
- `self.measures`, `self.button_layouts` (unused)
- Copy/paste fallback branch (pattern_widget always present)

---

### Phase 4 (Original): File-Level Change Summary

| File | Changes |
|------|---------|
| `jdxi_editor/ui/widgets/pattern/widget.py` | Add `_show_current_measure()`, `get_measure_widgets()`, optionally `set_button_click_handler()`, `ensure_measure_count()`, `clear_and_reset()`; apply sequencer styling |
| `jdxi_editor/ui/widgets/pattern/measure_widget.py` | Optionally accept styling callback or apply default `set_sequencer_style` |
| `jdxi_editor/ui/editors/pattern/ui.py` | Instantiate PatternWidget; replace `_create_measures_group` + `_create_sequencer_widget` with PatternWidget (or integrate its pieces); keep row headers in a layout that includes PatternWidget |
| `jdxi_editor/ui/editors/pattern/pattern.py` | Replace measure logic with delegation to `pattern_widget`; update `measure_widgets`, `measures_list`, `current_measure_index`, `total_measures` to use PatternWidget; wire callbacks |

---

### Phase 5: Implementation Order

1. **Step 1:** ✅ DONE – Extend PatternWidget so it populates `sequencer_display` with the current measure and apply sequencer styling.
2. **Step 2:** ✅ DONE – Add `get_measure_widgets()`, `ensure_measure_count()`, `clear_and_reset()` to PatternWidget.
3. **Step 3:** ✅ DONE – In PatternUI, create PatternWidget and place it in the splitter (replacing measures + sequencer).
4. **Step 4:** ✅ DONE – In PatternSequenceEditor, replace direct measure logic with `pattern_widget` calls.
5. **Step 5:** ✅ DONE – `self.buttons` delegates to PatternWidget's current measure (Phase 2).
6. **Step 6:** ✅ DONE – Removed dead `on_button_toggled`, `sync_ui_to_measure` from PatternSequenceEditor.
7. **Step 7:** ✅ DONE – Aligned clipboard format; PatternWidget copy reads from buttons; both formats supported for paste.

---

## 6. Method Signature Reference

### PatternWidget Additions

```python
def get_measure_widgets(self) -> list[PatternMeasureWidget]: ...

def ensure_measure_count(self, count: int) -> None:
    """Add or remove measures to match count."""

def clear_and_reset(self) -> None:
    """Clear all measures and list; optionally add one empty measure."""

def _show_current_measure(self) -> None:
    """Display current measure widget in sequencer_display."""

def set_button_click_handler(self, handler: Callable[[SequencerButton, bool], None] | None) -> None:
    """Optional: delegate button clicks to parent."""
```

### PatternSequenceEditor Delegations

```python
# Instead of self.measure_widgets:
self.pattern_widget.get_measure_widgets()

# Instead of self._add_measure():
self.pattern_widget.add_measure(copy_previous=self.copy_previous_measure_checkbox.isChecked())

# Instead of self.current_measure_index:
self.pattern_widget.current_measure_index

# Instead of self.measures_list:
self.pattern_widget.measures_list
```

---

## 7. Risk and Rollback

- **Risk:** Tight coupling between row headers, presets, mute, and the sequencer grid.
- **Mitigation:** Introduce PatternWidget behind a flag or adapter; keep old code paths until integration tests pass.
- **Rollback:** Revert to building `measure_widgets` and `measures_list` directly in PatternUI/PatternSequenceEditor if migration causes regressions.
