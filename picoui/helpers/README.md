# picoui helpers

Layout and group box helpers for PySide6 UI. Used by picoui widgets and by jdxi_editor.

## Layout (`layout.py`)

- **create_layout** – Create `QVBoxLayout` or `QHBoxLayout`, optionally with parent.
- **create_layout_with_widgets** – Row/column of widgets with optional stretches and spacing.
- **create_row_with_widgets** – Horizontal row with no stretches.
- **create_left_aligned_row** – Horizontal row with stretch only on the right.
- **create_vertical_layout** – `QVBoxLayout` with optional spacing/margins.
- **create_form_layout** – `QFormLayout` with zero margins, spacing 4.
- **create_header_row** – Row with an optional label (for headers).
- **create_layout_with_inner_layouts** – Outer layout containing inner layouts + bottom stretch.

## Groups (`groups.py`)

- **build_group** – `QGroupBox` with title and content: layout, list of widgets, single widget, or `None`.
- **group_with_layout** – `QGroupBox` plus a layout (create or pass in); returns `(group, layout)`.
- **group_from_definition** – Like `build_group` but takes a definition with `.label` and `.attr_name`, and can set the result on an object (`set_attr`).

## Usage

```python
from picoui.helpers import (
    build_group,
    create_layout_with_items,
    group_with_layout,
)

# Simple group with a list of widgets
group = build_group("Title", [widget1, widget2])

# Group and layout together (for adding more items to the layout later)
group, layout = group_with_layout(label="Section", vertical=True)
layout.addWidget(some_widget)
```

## Naming

- **build_*** / **group_with_*** – Preferred names in this package.
- **create_*** – Kept for layout helpers for consistency with existing code.
- jdxi_editor re-exports with backward-compatible names: `create_group` = `build_group`, `create_group_with_layout` = `group_with_layout`, `create_group_from_definition` = `group_from_definition`.
