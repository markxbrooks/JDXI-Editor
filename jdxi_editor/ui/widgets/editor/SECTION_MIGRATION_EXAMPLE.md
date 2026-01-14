# Section Icon Row Migration Guide

## Overview

The `SectionBaseWidget` class provides automatic icon row addition for all editor sections, ensuring consistency and reducing boilerplate code.

## Benefits

1. **Automatic icon rows**: Icon rows are added automatically based on section type
2. **Consistent structure**: All sections follow the same pattern
3. **Less boilerplate**: No need to manually add icon rows in each section
4. **Easy maintenance**: Change icon row logic in one place

## Migration Pattern

### Before (Manual Icon Row)

```python
class DigitalFilterSection(QWidget):
    def __init__(self, ...):
        super().__init__()
        # ... initialization ...
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        JDXiThemeManager.apply_adsr_style(self, analog=False)
        
        # Manual icon row addition
        icon_hlayout = IconRegistry.create_adsr_icons_row()
        layout.addLayout(icon_hlayout)
        
        # Rest of UI setup...
        layout.addWidget(my_widget)
```

### After (Automatic Icon Row)

```python
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget, IconType

class DigitalFilterSection(SectionBaseWidget):
    def __init__(self, ...):
        super().__init__(icon_type=IconType.ADSR, analog=False)
        # ... initialization ...
        self.setup_ui()
    
    def setup_ui(self):
        layout = self.get_layout()  # Icon row already added!
        
        # Rest of UI setup...
        layout.addWidget(my_widget)
```

## Icon Type Guide

- **`IconType.ADSR`**: For Filter, Amp, LFO, TVF, TVA, Pitch Env sections
- **`IconType.OSCILLATOR`**: For Oscillator sections
- **`IconType.GENERIC`**: For Common sections
- **`IconType.NONE`**: For sections that don't need icon rows

## Migration Steps

1. Change base class from `QWidget` to `SectionBaseWidget`
2. Update `__init__` to call `super().__init__(icon_type=..., analog=...)`
3. In `setup_ui()` or `init_ui()`, replace manual layout creation with `layout = self.get_layout()`
4. Remove manual icon row addition code
5. Remove manual `JDXiThemeManager.apply_adsr_style()` call (handled automatically)

## Example: Complete Migration

### Digital Filter Section

**Before:**
```python
class DigitalFilterSection(QWidget):
    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(5, 15, 5, 5)
        layout.setSpacing(5)
        JDXiThemeManager.apply_adsr_style(self, analog=False)
        
        # Icons
        icon_hlayout = IconRegistry.create_adsr_icons_row()
        layout.addLayout(icon_hlayout)
        
        # Rest of setup...
```

**After:**
```python
class DigitalFilterSection(SectionBaseWidget):
    def __init__(self, ...):
        super().__init__(icon_type=IconType.ADSR, analog=False)
        # ... rest of init ...
        self.setup_ui()
    
    def setup_ui(self):
        layout = self.get_layout()
        layout.setContentsMargins(5, 15, 5, 5)
        layout.setSpacing(5)
        
        # Rest of setup... (icon row already added!)
```

## Benefits Summary

- ✅ **Consistency**: All sections automatically get icon rows
- ✅ **DRY**: No repeated icon row code
- ✅ **Maintainability**: Change icon logic in one place
- ✅ **Type Safety**: IconType enum prevents typos
- ✅ **Flexibility**: Easy to disable icon rows with `IconType.NONE`
