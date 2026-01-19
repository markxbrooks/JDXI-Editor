# IconRegistry Refactoring Opportunities

This document identifies places in the codebase where `IconRegistry` could be used instead of direct `qta.icon()` calls.

## Current Status

The `IconRegistry` provides:
- Centralized icon definitions as constants
- Fallback support for missing icons
- Consistent icon loading with error handling
- Support for color and size parameters

## Opportunities for Refactoring

### 1. Playback Controls (High Priority)

**Current Pattern:**
```python
qta.icon("ri.play-line", color=JDXiStyle.FOREGROUND)
qta.icon("ri.stop-line", color=JDXiStyle.FOREGROUND)
qta.icon("ri.pause-line", color=JDXiStyle.FOREGROUND)
```

**Files Affected:**
- `jdxi_editor/ui/editors/io/player.py:602, 608, 614`
- `jdxi_editor/ui/editors/io/program.py:538, 541`

**Recommendation:** Use `IconRegistry.PLAY`, `IconRegistry.STOP`, `IconRegistry.PAUSE`

### 2. File Operations (High Priority)

**Current Pattern:**
```python
qta.icon("mdi.midi-port", color=JDXiStyle.FOREGROUND)  # Load/Save MIDI
qta.icon("ph.folder-notch-open-fill", color=JDXiStyle.FOREGROUND)  # Load Preset
qta.icon("ph.floppy-disk-fill", color=JDXiStyle.FOREGROUND)  # Save Changes
qta.icon("msc.folder-opened")  # Load Program
```

**Files Affected:**
- `jdxi_editor/ui/editors/io/player.py:223, 229`
- `jdxi_editor/ui/editors/io/program.py:478, 623, 1260`
- `jdxi_editor/ui/windows/jdxi/ui.py:232`

**Recommendation:** Use `IconRegistry.MIDI_PORT`, `IconRegistry.FOLDER_NOTCH_OPEN`, `IconRegistry.FLOPPY_DISK`, `IconRegistry.FOLDER_OPENED`

### 3. Menu Actions (High Priority)

**Current Pattern:**
```python
qta.icon("msc.settings")  # Preferences
qta.icon("mdi6.help-rhombus-outline")  # Documentation
```

**Files Affected:**
- `jdxi_editor/ui/windows/jdxi/ui.py:374, 380`

**Recommendation:** Use `IconRegistry.SETTINGS`, `IconRegistry.HELP_RHOMBUS`

### 4. Instrument Icons (Medium Priority)

**Current Pattern:**
```python
qta.icon("msc.piano", color=JDXiStyle.FOREGROUND).pixmap(40, 40)
qta.icon("fa5s.drum", color=JDXiStyle.FOREGROUND).pixmap(40, 40)
```

**Files Affected:**
- `jdxi_editor/ui/editors/io/program.py:839, 847, 856, 864`

**Recommendation:** Use `IconRegistry.get_icon_pixmap(IconRegistry.PIANO, ...)` or `IconRegistry.get_icon_pixmap(IconRegistry.DRUM, ...)`

### 5. Playlist Operations (Medium Priority)

**Current Pattern:**
```python
qta.icon("ph.plus-circle-fill", color=JDXiStyle.FOREGROUND)  # New Playlist
qta.icon("ph.trash-fill", color=JDXiStyle.FOREGROUND)  # Delete Playlist
qta.icon("ei.refresh", color=JDXiStyle.FOREGROUND)  # Refresh Playlist
```

**Files Affected:**
- `jdxi_editor/ui/editors/io/program.py:1560, 1566, 1572, 1881, 1891`

**Recommendation:** Use `IconRegistry.PLUS_CIRCLE`, `IconRegistry.TRASH_FILL`, `IconRegistry.REFRESH`

### 6. Add/Plus Icons (Medium Priority)

**Current Pattern:**
```python
qta.icon("mdi.plus", color=JDXiStyle.FOREGROUND)
```

**Files Affected:**
- `jdxi_editor/ui/editors/io/player.py:287`

**Recommendation:** Use `IconRegistry.ADD`

### 7. Synth Section Icons (Low Priority)

**Current Pattern:**
```python
qta.icon("mdi.triangle-wave", color="#666666")
qta.icon("ri.filter-3-fill", color="#666666")
qta.icon("mdi.amplifier", color="#666666")
qta.icon("mdi.sine-wave", color="#666666")
```

**Files Affected:**
- `jdxi_editor/ui/editors/analog/editor.py:251, 264, 275, 285`

**Recommendation:** Use `IconRegistry.TRIANGLE_WAVE`, `IconRegistry.FILTER`, `IconRegistry.AMPLIFIER`, `IconRegistry.SINE_WAVE`

### 8. ADSR Section Icons (Low Priority)

**Current Pattern:**
```python
qta.icon(icon, color="#666666").pixmap(30, 30)
```

**Files Affected:**
- `jdxi_editor/ui/editors/analog/filter.py:114`
- `jdxi_editor/ui/editors/analog/amp.py:122`
- `jdxi_editor/ui/editors/digital/partial/amp.py:101`

**Recommendation:** Use `IconRegistry.get_icon_pixmap()` with appropriate icon constants

### 9. Partial Panel Icons (Low Priority)

**Current Pattern:**
```python
qta.icon(f"mdi.numeric-{partial}-circle-outline", color="#666666")
```

**Files Affected:**
- `jdxi_editor/ui/widgets/panel/partial.py:39`

**Recommendation:** This is dynamic, but could use IconRegistry for the base pattern

### 10. Common Section Icons (Low Priority)

**Current Pattern:**
```python
qta.icon(icon_name, color="#666666")
```

**Files Affected:**
- `jdxi_editor/ui/editors/digital/common.py:53`
- `jdxi_editor/ui/editors/analog/common.py:53`

**Recommendation:** Add specific icon constants for these if they're commonly used

## Implementation Priority

1. **High Priority:** Playback controls, File operations, Menu actions (most common, easy wins)
2. **Medium Priority:** Instrument icons, Playlist operations, Add icons (frequently used)
3. **Low Priority:** Synth section icons, ADSR icons, Dynamic icons (may need more careful handling)

## Benefits of Refactoring

1. **Consistency:** Centralized icon definitions ensure consistent icon usage
2. **Maintainability:** Changes to icon names only need to be made in one place
3. **Type Safety:** Constants provide better IDE support and catch errors at development time
4. **Documentation:** Constant names serve as documentation for what icons are available
5. **Fallback Support:** IconRegistry provides automatic fallback for missing icons
6. **Error Handling:** Centralized error handling for icon loading failures

## Example Refactoring

**Before:**
```python
self.play_button = QPushButton(
    qta.icon("ri.play-line", color=JDXiStyle.FOREGROUND), "Play"
)
```

**After:**

```python
from jdxi_editor.ui.style.icons import JDXiUIIconRegistry

self.play_button = QPushButton(
    JDXiUIIconRegistry.get_icon(JDXiUIIconRegistry.PLAY, color=JDXiStyle.FOREGROUND), "Play"
)
```

Or for pixmaps:
```python
# Before
qta.icon("msc.piano", color=JDXiStyle.FOREGROUND).pixmap(40, 40)

# After
IconRegistry.get_icon_pixmap(IconRegistry.PIANO, color=JDXiStyle.FOREGROUND, size=40)
```
