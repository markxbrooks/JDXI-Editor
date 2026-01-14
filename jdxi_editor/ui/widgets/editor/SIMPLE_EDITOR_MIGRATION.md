# Simple Editor Migration Guide

## Overview

The `SimpleEditorHelper` class standardizes the setup of "Simple Editors" (Effects, Vocal Effects, Arpeggio) that follow a common pattern:
- Title + Image header
- Centered content layout  
- Tab widget with multiple sections
- Icon rows in each tab section

## Benefits

1. **Consistent Structure**: All simple editors follow the same pattern
2. **Less Boilerplate**: Reduces ~50+ lines of repetitive code per editor
3. **Easy Maintenance**: Change the pattern in one place
4. **Type Safety**: Clear API with getter methods

## Current Pattern (Before)

Each simple editor manually sets up:
- `EditorBaseWidget` and scrollable content
- `DigitalTitle` label
- `QLabel` for image
- `QGroupBox` for title group
- Centered content widget with `QHBoxLayout` (stretch, `QVBoxLayout`, stretch)
- `QTabWidget` creation and styling
- Adding centered content to base widget

**Example (Effects Editor):**
```python
# ~50 lines of boilerplate
self.base_widget = EditorBaseWidget(parent=self, analog=False)
self.base_widget.setup_scrollable_content()

if not hasattr(self, 'main_layout') or self.main_layout is None:
    self.main_layout = QVBoxLayout(self)
    self.setLayout(self.main_layout)
self.main_layout.addWidget(self.base_widget)

self.title_label = DigitalTitle("Effects")
JDXiThemeManager.apply_instrument_title_label(self.title_label)
self.image_label = QLabel()
self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
self.default_image = "effects.png"
self.instrument_icon_folder = "effects"
self.update_instrument_image()

title_group_box = QGroupBox()
title_group_layout = QHBoxLayout()
title_group_box.setLayout(title_group_layout)
title_group_layout.addWidget(self.title_label)
title_group_layout.addWidget(self.image_label)

centered_content = QWidget()
main_row_hlayout = QHBoxLayout(centered_content)
main_row_hlayout.addStretch()
rows_layout = QVBoxLayout()
main_row_hlayout.addLayout(rows_layout)
rows_layout.addWidget(title_group_box)

self.tabs = QTabWidget()
JDXiThemeManager.apply_tabs_style(self.tabs)
rows_layout.addWidget(self.tabs)

main_row_hlayout.addStretch()
self.base_widget.add_centered_content(centered_content)
```

## New Pattern (After)

Using `SimpleEditorHelper`:

```python
from jdxi_editor.ui.widgets.editor.simple_editor_helper import SimpleEditorHelper

class EffectsCommonEditor(BasicEditor):
    def __init__(self, midi_helper, preset_helper=None, parent=None):
        super().__init__(midi_helper=midi_helper, parent=parent)
        
        # Setup base widget
        self.base_widget = EditorBaseWidget(parent=self, analog=False)
        self.base_widget.setup_scrollable_content()
        
        # Use helper to setup title/image and tabbed content
        self.editor_helper = SimpleEditorHelper(
            editor=self,
            base_widget=self.base_widget,
            title="Effects",
            image_folder="effects",
            default_image="effects.png"
        )
        
        # Create tabs
        self.tabs = self.editor_helper.get_tab_widget()
        self.tabs.addTab(self._create_effect1_section(), "Effect 1")
        self.tabs.addTab(self._create_effect2_section(), "Effect 2")
        self.tabs.addTab(self._create_delay_tab(), "Delay")
        self.tabs.addTab(self._create_reverb_section(), "Reverb")
        
        # Add base widget to editor's layout
        if not hasattr(self, 'main_layout') or self.main_layout is None:
            self.main_layout = QVBoxLayout(self)
            self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.base_widget)
        
        # ... rest of initialization
```

## Migration Steps

1. Import `SimpleEditorHelper`
2. Replace manual title/image/tab setup with `SimpleEditorHelper` instantiation
3. Use `editor_helper.get_tab_widget()` instead of manually creating `QTabWidget`
4. Remove manual title/image/tab setup code (~50 lines)
5. Access title/image labels via helper if needed: `editor_helper.get_title_label()`

## API Reference

### `SimpleEditorHelper.__init__(editor, base_widget, title, image_folder, default_image)`

Initialize the helper with editor reference and configuration.

**Parameters:**
- `editor`: The editor widget (typically a BasicEditor subclass)
- `base_widget`: The EditorBaseWidget instance
- `title`: Title text for the editor
- `image_folder`: Folder name for instrument images
- `default_image`: Default image filename

### `get_tab_widget() -> QTabWidget`

Get the tab widget for adding tabs.

### `get_rows_layout() -> QVBoxLayout`

Get the rows layout (contains title group and tab widget).

### `get_title_label() -> DigitalTitle`

Get the title label.

### `get_image_label() -> QLabel`

Get the image label.

## Editors to Migrate

1. **EffectsCommonEditor** (`jdxi_editor/ui/editors/effects/common.py`)
2. **VocalFXEditor** (`jdxi_editor/ui/editors/effects/vocal.py`)
3. **ArpeggioEditor** (`jdxi_editor/ui/editors/arpeggio/arpeggio.py`)

## Benefits Summary

- ✅ **Consistency**: All simple editors use the same pattern
- ✅ **DRY**: ~150 lines of boilerplate removed across 3 editors
- ✅ **Maintainability**: Change pattern in one place
- ✅ **Clarity**: Clear API with descriptive method names
- ✅ **Flexibility**: Can still access individual components via getters
