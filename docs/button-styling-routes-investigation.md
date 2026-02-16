# Button styling routes: Oscillator, Mode buttons, Mod LFO, LFO, Filter (Analog & Digital)

Investigation of where init and selection styling are applied for the five control types, with harmonisation to a single Theme API.

## Intended standard (harmonised)

- **Default (unselected):** `JDXi.UI.Theme.apply_button_rect(btn, analog=<bool>)`
- **Selected/active:** `JDXi.UI.Theme.apply_button_active(btn, analog=<bool>)`
- **Context:** `analog=True` → Analog editor/section (blue styles). `analog=False` → Digital (gray BUTTON_RECT / BUTTON_RECT_ACTIVE).

No direct `setStyleSheet(JDXi.UI.Style.BUTTON_*)` or `apply_button_analog_active` in these flows; use `apply_button_active(btn, analog=...)` so one API covers both contexts.

---

## 1. Oscillator (waveform buttons)

| Context | Init | On click / selection | Preset/SysEx update |
|--------|------|----------------------|--------------------|
| **Analog** | `base/oscillator/section`: ModeButtonGroup `_build_button` → `Theme.apply_button_rect(btn, analog=True)`. Manual path same. | ModeButtonGroup `set_mode` → `apply_button_rect` + `apply_button_active(analog)`. Section `_on_button_selected` same. | `base/editor`: `_on_waveform_selected` / `_update_waveform_buttons` → `apply_button_rect` + `apply_button_active(analog)` ✓ |
| **Digital** | Same via ModeButtonGroup with `analog=False`. | ModeButtonGroup `set_mode`. | `digital/editor` `_update_waveform_buttons`: Theme API when styling directly; else `wave_mode_group.set_mode()`. ✓ |

**Status:** Harmonised (Theme API throughout).

---

## 2. Mode buttons (ModeButtonGroup – waveform row)

Same as Oscillator when used for waveforms (Analog oscillator, Digital oscillator). Implemented in `ui/widgets/editor/mode_button_group.py`:

- Init: `Theme.apply_button_rect(btn, analog=self._analog)`
- Selection: `apply_button_rect(b, analog=self._analog)` for others, `apply_button_active(btn, analog=self._analog)` for selected.

**Status:** Harmonised.

---

## 3. Mod LFO (shape buttons)

Mod LFO exists only in Digital.

| Context | Init | On click | Preset/SysEx update |
|--------|------|----------|---------------------|
| **Digital** | `section_base._create_shape_row()` → `Theme.apply_button_rect(btn, analog=self.analog)` (section has `analog=False`). | `_on_shape_group_changed` → `set_wave_shape` → `_apply_wave_shape_style`: reset all with `apply_button_rect`, active with `apply_button_active(analog)`. | `digital/editor._update_mod_lfo_shape_buttons` → Theme API ✓ |

**Status:** Harmonised.

---

## 4. LFO (shape buttons)

| Context | Init | On click | Preset/SysEx update |
|--------|------|----------|---------------------|
| **Analog** | `section_base._create_shape_row()` with `analog=True`. | `_apply_wave_shape_style` (Theme API). | `base/editor`: `_on_lfo_shape_changed` uses `apply_button_rect` + **`apply_button_analog_active(selected_btn)`**. `_update_lfo_shape_buttons` same. |
| **Digital** | Same section_base path, `analog=False`. | Same `_apply_wave_shape_style`. | `digital/editor._update_lfo_shape_buttons` → Theme API ✓ |

**Status:** Analog editor still uses `apply_button_analog_active`; should use `apply_button_active(selected_btn, analog=self.analog)`.

---

## 5. Filter mode buttons

| Context | Init | On click | Preset/SysEx update |
|--------|------|----------|---------------------|
| **Analog** | `base/filter/filter._create_filter_controls_row` → `set_button_style_and_dimensions(btn, WaveformIcon)`. Helper does `apply_button_rect(btn, analog=self.analog)` but **`self` is undefined** in module-level helper (bug). | `base/filter/filter._on_filter_mode_selected` → `apply_button_rect(btn, analog=self.analog)` + **`apply_button_analog_active(selected_btn)`**. | `base/editor._update_filter_mode_buttons` → `apply_button_rect` + **`apply_button_analog_active(selected_btn)`**. |
| **Digital** | Same filter base class; `analog=False` in Digital section. Same broken helper call. | Same section method. | `digital/editor._update_filter_mode_buttons` → Theme API ✓ |

**Status:**

- Init: Helper `set_button_style_and_dimensions` must take `analog` (or caller applies theme after dimensions).
- Section and base editor: replace `apply_button_analog_active` with `apply_button_active(selected_btn, analog=self.analog)`.

---

## Other flows (panel waveform selection)

- **base/panel.py** and **digital/partial/panel.py** `_on_waveform_selected`: use **`setStyleSheet(BUTTON_RECT)`** and **`setStyleSheet(BUTTON_RECT_ACTIVE)`** for waveform buttons when user selects from panel. Should use Theme API for consistency.

---

## Harmonisation checklist (done)

1. **base/editor.py** ✓  
   - `_update_filter_mode_buttons`, `_on_lfo_shape_changed`, `_update_lfo_shape_buttons`: use `apply_button_active(selected_btn, analog=self.analog)`.

2. **base/filter/filter.py** ✓  
   - `_on_filter_mode_selected`: use `apply_button_active(selected_btn, analog=self.analog)`.

3. **helper.py** ✓  
   - `set_button_style_and_dimensions(btn, dimensions, *, analog=False)`: added `analog` parameter; uses `Theme.apply_button_rect(btn, analog=analog)`.

4. **base/filter/filter.py** (init) ✓  
   - Calls `set_button_style_and_dimensions(btn, JDXi.UI.Dimensions.WaveformIcon, analog=self.analog)`.

5. **base/panel.py** and **digital/partial/panel.py** ✓  
   - `_on_waveform_selected`: use `Theme.apply_button_rect(btn, analog=False)` and `Theme.apply_button_active(selected, analog=False)`.

After these changes, all five control types use the same Theme API on init and on selection in both Analog and Digital editors.
