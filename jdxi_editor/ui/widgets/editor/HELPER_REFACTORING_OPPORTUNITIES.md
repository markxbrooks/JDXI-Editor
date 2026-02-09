# Helper Refactoring Opportunities

This document identifies opportunities to use existing helper functions and suggests new helpers to reduce code duplication and improve UI consistency across the codebase.

## Current Helper Functions

The helpers in `jdxi_editor/ui/widgets/editor/helper.py` provide:
- Layout creation with consistent patterns
- Group box creation with layouts
- Form layout creation with widgets
- Scroll area creation
- ADSR envelope group creation
- Centered layouts with stretches
- Icon creation and layout

## Duplication Patterns Found

### 1. Manual Form Layout Creation ⚠️ **HIGH IMPACT**

**Pattern Found:** Many places manually create `QGroupBox()` and `QFormLayout()` separately.

**Current Code (Duplicated ~16+ times):**
```python
# Example from drum/partial/partial.py
partial_misc_group = QGroupBox()
form_layout = QFormLayout()
partial_misc_group.setLayout(form_layout)
form_layout.addRow(widget1)
form_layout.addRow(widget2)
```

**Should Use:**

```python
from jdxi_editor.ui.widgets.editor.helper import create_group_with_layout, create_form_layout_with_widgets

# Option 1: Create group with form layout
partial_misc_group, form_layout = create_group_with_layout(
    label="Misc",
    child_layout=create_form_layout_with_widgets([widget1, widget2])
)

# Option 2: Even simpler - create form layout with widgets first
form_layout = create_form_layout_with_widgets([widget1, widget2])
partial_misc_group, _ = create_group_with_layout("Misc", child_layout=form_layout)
```

**Files Affected:**
- `jdxi_editor/ui/editors/drum/partial/partial.py` (4 instances)
- `jdxi_editor/ui/editors/drum/partial/tvf.py` (1 instance)
- `jdxi_editor/ui/editors/drum/partial/wmt.py` (5 instances)
- Many other editor files

**Impact:** ~20+ instances could be simplified

---

### 2. Manual Centered Layout Creation ⚠️ **MEDIUM IMPACT**

**Pattern Found:** Manual creation of `QHBoxLayout()` with stretches for centering.

**Current Code (Duplicated ~10+ times):**
```python
# Example from analog/section.py
filter_row = QHBoxLayout()
filter_row.addStretch()
filter_row.addWidget(label)
filter_row.addWidget(button1)
filter_row.addWidget(button2)
filter_row.addStretch()
```

**Should Use:**
```python
from jdxi_editor.ui.widgets.editor.helper import create_layout_with_widgets

filter_row = create_layout_with_widgets([label, button1, button2], vertical=False)
```

**Files Affected:**
- `jdxi_editor/ui/editors/analog/filter.py`
- `jdxi_editor/ui/editors/digital/partial/filter.py`
- `jdxi_editor/ui/editors/digital/common.py`
- `jdxi_editor/ui/editors/io/program.py` (multiple instances)
- `jdxi_editor/ui/editors/io/preset.py` (multiple instances)

**Impact:** ~15+ instances could be simplified

---

### 3. Manual Scroll Area Creation ⚠️ **MEDIUM IMPACT**

**Pattern Found:** Manual creation of scroll areas with identical settings.

**Current Code (Duplicated ~5+ times):**
```python
# Example from drum/partial/wmt.py
scroll_area = QScrollArea()
scroll_area.setWidgetResizable(True)
scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
scrolled_widget = QWidget()
scrolled_layout = QVBoxLayout(scrolled_widget)
scroll_area.setWidget(scrolled_widget)
```

**Should Use:**
```python
from jdxi_editor.ui.widgets.editor.helper import create_scrolled_area_with_layout

scroll_area, scrolled_layout = create_scrolled_area_with_layout()
```

**Files Affected:**
- `jdxi_editor/ui/editors/drum/partial/wmt.py`
- Other sections that manually create scroll areas

**Impact:** ~5-10 instances could be simplified

---

### 4. Manual ADSR Group Creation ⚠️ **LOW-MEDIUM IMPACT**

**Pattern Found:** Some places manually create ADSR envelope groups instead of using `create_envelope_group()`.

**Current Code:**
```python
# Example from drum/partial/tvf.py
envelope_group = QGroupBox("Envelope")
envelope_group_layout = QHBoxLayout()
envelope_group.setLayout(envelope_group_layout)
envelope_group.setStyleSheet(JDXiStyle.ADSR)
# ... manual icon and widget setup
```

**Should Use:**
```python
from jdxi_editor.ui.widgets.editor.helper import create_envelope_group

envelope_group = create_envelope_group(
    name="Envelope",
    adsr_widget=adsr_widget,
    analog=False  # or True for analog sections
)
```

**Files Affected:**
- `jdxi_editor/ui/editors/drum/partial/tvf.py`
- Potentially other envelope sections

**Impact:** ~3-5 instances could be simplified

---

## New Helper Functions Added ✅

### 1. `create_group_with_form_layout(widgets: list, group_name: str = None) -> tuple[QGroupBox, QFormLayout]` ✅

**Status:** ✅ **ADDED** to `helper.py`

**Purpose:** Combine `create_group_with_layout()` and `create_form_layout_with_widgets()` into one call.

**Usage:**

```python
from jdxi_editor.ui.widgets.editor.helper import create_group_with_form_layout

group, form_layout = create_group_with_form_layout(
    widgets=[widget1, widget2, widget3],
    label="Controls"
)
```

**Benefits:**
- Reduces 3-4 lines to 1 line
- Ensures consistent form layout creation
- Makes code more readable

---

### 2. `create_left_aligned_row(widgets: list) -> QHBoxLayout` ✅

**Status:** ✅ **ADDED** to `helper.py`

**Purpose:** Create a left-aligned horizontal layout (stretch only on the right).

**Usage:**
```python
from jdxi_editor.ui.widgets.editor.helper import create_left_aligned_row

row = create_left_aligned_row([label, button1, button2])
# Result: [widget1, widget2, widget3] [stretch]
```

**Benefits:**
- Previously defined locally in ArpeggioEditor - now available globally
- Could be used in filter control rows
- More semantic than manual layout creation

---

### 3. `create_centered_group(group_name: str, widgets: list, vertical: bool = True) -> QGroupBox`

**Purpose:** Create a group box with centered content.

**Usage:**
```python
group = create_centered_group(
    group_name="Controls",
    widgets=[widget1, widget2],
    vertical=True
)
```

**Benefits:**
- Combines group creation with centered layout
- Reduces boilerplate for centered groups

---

### 4. `create_tab_widget_with_tabs(tabs: list[tuple[str, QWidget, QIcon]]) -> QTabWidget`

**Purpose:** Create a tab widget and add multiple tabs in one call.

**Usage:**
```python
tab_widget = create_tab_widget_with_tabs([
    ("Controls", controls_widget, controls_icon),
    ("ADSR", adsr_widget, adsr_icon),
    ("Pan", pan_widget, pan_icon),
])
```

**Benefits:**
- Reduces repetitive `addTab()` calls
- Ensures consistent tab creation

---

## Refactoring Priority

### High Priority (Immediate Impact)
1. **Form Layout Creation** - ~20+ instances
   - Use `create_group_with_layout()` + `create_form_layout_with_widgets()`
   - Or create new `create_group_with_form_layout()` helper

2. **Centered Layout Creation** - ~15+ instances
   - Use `create_layout_with_widgets()` with `vertical=False`

### Medium Priority (Good ROI)
3. **Scroll Area Creation** - ~5-10 instances
   - Use `create_scrolled_area_with_layout()`

4. **ADSR Group Creation** - ~3-5 instances
   - Use `create_envelope_group()`

### Low Priority (Nice to Have)
5. **Tab Widget Creation** - Could create helper for multiple tabs
6. **Group Box Patterns** - Could create more specialized group helpers

---

## Example Refactoring

### Before (drum/partial/partial.py):
```python
def _create_partial_misc_group(self) -> QGroupBox:
    """create partial misc group"""
    partial_misc_group = QGroupBox()
    form_layout = QFormLayout()
    partial_misc_group.setLayout(form_layout)

    partial_env_mode_combo = self._create_parameter_combo_box(...)
    form_layout.addRow(partial_env_mode_combo)

    pitch_bend_range_slider = self._create_parameter_slider(...)
    form_layout.addRow(pitch_bend_range_slider)

    assign_type_combo = self._create_parameter_combo_box(...)
    form_layout.addRow(assign_type_combo)

    mute_group_combo = self._create_parameter_combo_box(...)
    form_layout.addRow(mute_group_combo)

    partial_level_slider = self._create_parameter_slider(...)
    form_layout.addRow(partial_level_slider)
    return partial_misc_group
```

### After (Using Helpers):
```python
def _create_partial_misc_group(self) -> QGroupBox:
    """create partial misc group"""
    widgets = [
        self._create_parameter_combo_box(DrumPartialParam.PARTIAL_ENV_MODE, "Partial Env Mode", ["NO-SUS", "SUSTAIN"], [0, 1]),
        self._create_parameter_slider(DrumPartialParam.PARTIAL_PITCH_BEND_RANGE, "Pitch Bend Range"),
        self._create_parameter_combo_box(DrumPartialParam.ASSIGN_TYPE, "Assign Type", ["MULTI", "SINGLE"], [0, 1]),
        self._create_parameter_combo_box(DrumPartialParam.MUTE_GROUP, "Mute Group", ["OFF"] + [str(i) for i in range(1, 31)], list(range(0, 31))),
        self._create_parameter_slider(DrumPartialParam.PARTIAL_LEVEL, "Partial Level"),
    ]
    group, _ = create_group_with_form_layout(widgets, group_name="Misc")
    return group
```

**Benefits:**
- Reduced from ~15 lines to ~8 lines
- More readable
- Consistent with other sections
- Easier to maintain

---

## Concrete Refactoring Examples

### Example 1: Form Layout Creation (drum/partial/partial.py)

**Before:**
```python
def _create_partial_misc_group(self) -> QGroupBox:
    partial_misc_group = QGroupBox()
    form_layout = QFormLayout()
    partial_misc_group.setLayout(form_layout)
    
    partial_env_mode_combo = self._create_parameter_combo_box(...)
    form_layout.addRow(partial_env_mode_combo)
    
    pitch_bend_range_slider = self._create_parameter_slider(...)
    form_layout.addRow(pitch_bend_range_slider)
    
    assign_type_combo = self._create_parameter_combo_box(...)
    form_layout.addRow(assign_type_combo)
    
    mute_group_combo = self._create_parameter_combo_box(...)
    form_layout.addRow(mute_group_combo)
    
    partial_level_slider = self._create_parameter_slider(...)
    form_layout.addRow(partial_level_slider)
    return partial_misc_group
```

**After:**
```python
def _create_partial_misc_group(self) -> QGroupBox:
    widgets = [
        self._create_parameter_combo_box(DrumPartialParam.PARTIAL_ENV_MODE, "Partial Env Mode", ["NO-SUS", "SUSTAIN"], [0, 1]),
        self._create_parameter_slider(DrumPartialParam.PARTIAL_PITCH_BEND_RANGE, "Pitch Bend Range"),
        self._create_parameter_combo_box(DrumPartialParam.ASSIGN_TYPE, "Assign Type", ["MULTI", "SINGLE"], [0, 1]),
        self._create_parameter_combo_box(DrumPartialParam.MUTE_GROUP, "Mute Group", ["OFF"] + [str(i) for i in range(1, 31)], list(range(0, 31))),
        self._create_parameter_slider(DrumPartialParam.PARTIAL_LEVEL, "Partial Level"),
    ]
    group, _ = create_group_with_form_layout(widgets, group_name="Misc")
    return group
```

**Savings:** 15 lines → 8 lines (47% reduction)

---

### Example 2: Centered Layout (analog/filter.py)

**Before:**
```python
def _create_filter_controls_row(self) -> QHBoxLayout:
    filter_row = QHBoxLayout()
    filter_row.addStretch()
    
    filter_label = QLabel("Filter")
    filter_row.addWidget(filter_label)
    
    for filter_mode in filter_modes:
        btn = QPushButton(filter_mode.name)
        # ... setup button ...
        filter_row.addWidget(btn)
    
    filter_row.addStretch()
    return filter_row
```

**After:**
```python
def _create_filter_controls_row(self) -> QHBoxLayout:
    widgets = [QLabel("Filter")]
    for filter_mode in filter_modes:
        btn = QPushButton(filter_mode.name)
        # ... setup button ...
        widgets.append(btn)
    return create_layout_with_widgets(widgets, vertical=False)
```

**Savings:** 8 lines → 6 lines (25% reduction)

---

### Example 3: Left-Aligned Row (arpeggio/arpeggio.py)

**Before:**
```python
def create_left_aligned_row(widget_list: list) -> QHBoxLayout:
    """Create a left-aligned horizontal layout"""
    row = QHBoxLayout()
    for widget in widget_list:
        row.addWidget(widget)
    row.addStretch()
    return row

style_row = create_left_aligned_row([self.style_combo])
```

**After:**
```python
from jdxi_editor.ui.widgets.editor.helper import create_left_aligned_row

style_row = create_left_aligned_row([self.style_combo])
```

**Savings:** Removes local function definition, uses shared helper

---

### Example 4: Scroll Area (drum/partial/wmt.py)

**Before:**
```python
scroll_area = QScrollArea()
scroll_area.setWidgetResizable(True)
scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
scrolled_widget = QWidget()
scrolled_layout = QVBoxLayout(scrolled_widget)
scroll_area.setWidget(scrolled_widget)
```

**After:**
```python
from jdxi_editor.ui.widgets.editor.helper import create_scrolled_area_with_layout

scroll_area, scrolled_layout = create_scrolled_area_with_layout()
```

**Savings:** 8 lines → 2 lines (75% reduction)

---

## Summary

The existing helpers are already very useful, and with the **2 new helpers added**, there are **~40-50 instances** of duplication that could be eliminated by:

1. ✅ **Using existing helpers** where they're not currently used
2. ✅ **Using new helper functions** (`create_group_with_form_layout`, `create_left_aligned_row`)
3. **Refactoring existing code** to use helpers consistently

### Impact Metrics:

- **Form Layout Creation:** ~20 instances → Use `create_group_with_form_layout()`
- **Centered Layout Creation:** ~15 instances → Use `create_layout_with_widgets()`
- **Scroll Area Creation:** ~5-10 instances → Use `create_scrolled_area_with_layout()`
- **Left-Aligned Rows:** ~8 instances → Use `create_left_aligned_row()`

### Expected Results:

- **~30-40% reduction** in boilerplate code
- **Improved consistency** across all editors
- **Easier maintenance** - changes to patterns only need to be made in one place
- **Better readability** - intent is clearer with semantic helper names
- **Fewer bugs** - standardized patterns reduce chance of errors

### Next Steps:

1. **Refactor high-impact areas first:**
   - `drum/partial/partial.py` - 4 form layout groups
   - `drum/partial/wmt.py` - 5 form layout groups + scroll area
   - `analog/filter.py` - centered layout
   - `digital/partial/filter.py` - centered layout

2. **Update ArpeggioEditor** to use shared `create_left_aligned_row()` helper

3. **Gradually refactor** other editors as code is touched