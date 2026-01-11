# ThemeManager Refactoring Opportunities

This document identifies places in the codebase where `JDXiThemeManager` could be used instead of direct `setStyleSheet()` calls with `JDXiStyle` constants.

## Current Status

The `JDXiThemeManager` provides several convenience methods:
- `apply_editor_title_label()` - for editor title labels
- `apply_analog_section_header()` - for analog section headers
- `apply_digital_section_header()` - for digital section headers
- `apply_midi_monitor()` - for MIDI message monitors
- `apply_status_indicator_active()` - for active status indicators
- `apply_status_indicator_inactive()` - for inactive status indicators
- `apply_button_glow_red()` - for red glow buttons
- `apply_button_glow_analog()` - for analog (blue) glow buttons
- `apply_waveform_button()` - for waveform buttons
- `apply_instrument_background()` - for instrument backgrounds
- `apply_table_style()` - for table widgets

## Opportunities for Refactoring

### 1. Editor Styles (High Priority)

**Current Pattern:**
```python
self.setStyleSheet(JDXiStyle.EDITOR)
```

**Files Affected:**
- `jdxi_editor/ui/editors/pattern/pattern.py:98`
- `jdxi_editor/ui/editors/synth/editor.py:138`

**Recommendation:** Add `apply_editor_style()` method to ThemeManager

### 2. Title Labels (High Priority)

**Current Pattern:**
```python
self.title_label.setStyleSheet(JDXiStyle.INSTRUMENT_TITLE_LABEL)
self.title_label.setStyleSheet(JDXiStyle.EDITOR_TITLE_LABEL)
```

**Files Affected:**
- `jdxi_editor/ui/editors/effects/common.py:275`
- `jdxi_editor/ui/editors/effects/vocal.py:109`
- `jdxi_editor/ui/editors/arpeggio/arpeggio.py:119`

**Recommendation:** Use existing `apply_editor_title_label()` method, or add `apply_instrument_title_label()` if different from editor title

### 3. Mixer Labels (Medium Priority)

**Current Pattern:**
```python
self.master_level_title.setStyleSheet(JDXiStyle.MIXER_LABEL)
self.digital_synth_1_title.setStyleSheet(JDXiStyle.MIXER_LABEL)
self.analog_synth_title.setStyleSheet(JDXiStyle.MIXER_LABEL_ANALOG)
```

**Files Affected:**
- `jdxi_editor/ui/editors/io/program.py:833-868` (multiple instances)

**Recommendation:** Add `apply_mixer_label()` and `apply_mixer_label_analog()` methods

### 4. Checkbox/Switch Styles (Medium Priority)

**Current Pattern:**
```python
checkbox.setStyleSheet(JDXiStyle.PARTIAL_SWITCH)
```

**Files Affected:**
- `jdxi_editor/ui/editors/io/player.py:237, 249, 500, 513`

**Recommendation:** Add `apply_partial_switch()` method

### 5. ADSR Styles (Medium Priority)

**Current Pattern:**
```python
widget.setStyleSheet(JDXiStyle.ADSR)
widget.setStyleSheet(JDXiStyle.ADSR_ANALOG)
widget.setStyleSheet(JDXiStyle.ADSR_PLOT)
widget.setStyleSheet(JDXiStyle.ADSR_DISABLED)
```

**Files Affected:**
- Multiple files in `jdxi_editor/ui/editors/digital/partial/`
- Multiple files in `jdxi_editor/ui/editors/analog/`
- Multiple files in `jdxi_editor/ui/editors/drum/partial/`
- `jdxi_editor/ui/widgets/filter/analog_filter_plot.py:110`
- `jdxi_editor/ui/widgets/filter/filter_plot.py:110`
- `jdxi_editor/ui/widgets/wmt/envelope_plot.py:75`
- `jdxi_editor/ui/editors/drum/partial/pitch_env.py:86`
- `jdxi_editor/ui/editors/drum/partial/tvf.py:87`

**Recommendation:** Add `apply_adsr_style()`, `apply_adsr_analog()`, `apply_adsr_plot()`, `apply_adsr_disabled()` methods

### 6. Tab Styles (Medium Priority)

**Current Pattern:**
```python
self.tabs.setStyleSheet(JDXiStyle.TABS)
self.setStyleSheet(JDXiStyle.TABS + JDXiStyle.EDITOR)
self.setStyleSheet(JDXiStyle.TABS_ANALOG + JDXiStyle.EDITOR_ANALOG)
```

**Files Affected:**
- `jdxi_editor/ui/editors/effects/common.py:307`
- `jdxi_editor/ui/editors/effects/vocal.py:82`
- `jdxi_editor/ui/editors/digital/editor.py:153, 166, 222`

**Recommendation:** Add `apply_tabs_style()`, `apply_tabs_analog_style()` methods

### 7. Button Styles (Low Priority - Many Dynamic Cases)

**Current Pattern:**
```python
btn.setStyleSheet(JDXiStyle.BUTTON_RECT)
btn.setStyleSheet(JDXiStyle.BUTTON_RECT_ACTIVE)
btn.setStyleSheet(JDXiStyle.BUTTON_RECT_ANALOG)
btn.setStyleSheet(JDXiStyle.BUTTON_ANALOG_ACTIVE)
```

**Files Affected:**
- Many files in `jdxi_editor/ui/editors/digital/partial/oscillator.py`
- Many files in `jdxi_editor/ui/editors/analog/oscillator.py`
- `jdxi_editor/ui/editors/digital/editor.py:730, 736`

**Recommendation:** Add `apply_button_rect()`, `apply_button_rect_active()`, `apply_button_rect_analog()`, `apply_button_analog_active()` methods

### 8. Window Styles (Low Priority)

**Current Pattern:**
```python
self.setStyleSheet(JDXiStyle.TRANSPARENT + JDXiStyle.ADSR_DISABLED)
self.setStyleSheet(JDXiStyle.DEBUGGER)
status_bar.setStyleSheet(JDXiStyle.TRANSPARENT)
```

**Files Affected:**
- `jdxi_editor/ui/windows/jdxi/instrument.py:125`
- `jdxi_editor/ui/windows/midi/debugger.py:141`
- `jdxi_editor/ui/windows/jdxi/ui.py:395`

**Recommendation:** Add `apply_transparent()`, `apply_debugger_window()` methods

### 9. Combo Box Styles (Low Priority)

**Current Pattern:**
```python
self.instrument_selection_combo.setStyleSheet(JDXiStyle.COMBO_BOX_ANALOG)
self.instrument_selection_combo.setStyleSheet(JDXiStyle.COMBO_BOX)
```

**Files Affected:**
- `jdxi_editor/ui/editors/synth/editor.py:264, 266`

**Recommendation:** Add `apply_combo_box()` and `apply_combo_box_analog()` methods

### 10. Line Edit Styles (Low Priority)

**Current Pattern:**
```python
self.search_box.setStyleSheet(JDXiStyle.QLINEEDIT)
```

**Files Affected:**
- `jdxi_editor/ui/editors/io/program.py:455, 589`

**Recommendation:** Add `apply_line_edit()` method

## Implementation Priority

1. **High Priority:** Editor styles, Title labels (most common, easy wins)
2. **Medium Priority:** ADSR styles, Tab styles, Mixer labels, Checkbox styles (frequently used)
3. **Low Priority:** Button styles, Window styles, Combo box styles (many dynamic cases, may need more careful handling)

## Benefits of Refactoring

1. **Consistency:** Centralized styling ensures consistent application of styles
2. **Maintainability:** Changes to styles only need to be made in one place
3. **Type Safety:** Methods provide better IDE support and catch errors at development time
4. **Documentation:** Method names serve as documentation for what styles are available
5. **Future Flexibility:** Easy to add theme switching, style variants, or dynamic styling

## Example Refactoring

**Before:**
```python
self.setStyleSheet(JDXiStyle.EDITOR)
self.title_label.setStyleSheet(JDXiStyle.INSTRUMENT_TITLE_LABEL)
checkbox.setStyleSheet(JDXiStyle.PARTIAL_SWITCH)
```

**After:**
```python
JDXiThemeManager.apply_editor_style(self)
JDXiThemeManager.apply_instrument_title_label(self.title_label)
JDXiThemeManager.apply_partial_switch(checkbox)
```
