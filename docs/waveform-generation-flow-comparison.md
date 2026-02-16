# Waveform / Shape Generation Flow Comparison

Comparison of how **waveform** (oscillator) and **wave shape** (LFO, Mod LFO) selection is built and updated in Analog vs Digital synths, with a view to harmonizing them.

---

## 1) Oscillator (waveform selection)

| Aspect | Analog Oscillator | Digital Oscillator |
|--------|-------------------|--------------------|
| **Spec type** | `SliderSpec(param=W.Osc.*, label, icon_name)` | Same: `SliderSpec(param=W.Osc.*, label, icon_name)` |
| **Spec source** | `AnalogOscillatorSection.generate_wave_shapes()` (3 shapes: SAW, TRI, SQUARE) | `DigitalOscillatorSection.generate_wave_shapes()` (more shapes: SAW, SQUARE, PWSQU, TRI, SINE, NOISE, SUPER_SAW, PCM) |
| **When specs set** | Before `super().__init__`: `self.wave_shapes = self.generate_wave_shapes()` | Before `super().__init__`: `self.wave_shapes = self.generate_wave_shapes()` |
| **Who creates buttons** | `BaseOscillatorSection._create_waveform_buttons()` (override in base/oscillator/section.py): builds `QPushButton`s, adds to `wave_button_group` (QButtonGroup), stores in `waveform_buttons`, `button_widgets`, `wave_layout_widgets` | `DigitalOscillatorSection._create_waveform_buttons()` (override): builds **ModeButtonGroup**(specs) (reusable widget that embeds a QButtonGroup); exposes `waveform_buttons = mode_button_group.buttons` |
| **Exclusivity** | `QButtonGroup` in base (`wave_button_group.setExclusive(True)`) | `ModeButtonGroup` embeds `QButtonGroup` with `setExclusive(True)` |
| **Init/layout flow** | Uses default `SectionBaseWidget` path: `__init__` → `build_widgets()` (base calls `_get_button_specs()` → `_create_waveform_buttons()`; oscillator overrides `build_widgets()` and calls `self._create_waveform_buttons()` first, then parent). No `SKIP_BASE_SETUP_UI`. `setup_ui()` overridden in base oscillator: adds `_create_wave_layout()` (wave row) then tab_widget | Same base flow; `build_widgets()` creates `ModeButtonGroup` via `_create_waveform_buttons()` then `super().build_widgets()`. `_setup_ui()` overridden: adds `wave_mode_group` row then tab_widget |
| **Stored refs** | `waveform_buttons` (param→btn), `button_widgets` (btn_key→btn), `wave_layout_widgets`, `wave_button_group` | `wave_mode_group`, `waveform_buttons` (= `wave_mode_group.buttons`), `wave_layout_widgets` |

**Summary (Oscillator):** Same spec shape (`SliderSpec`) and “specs before super” pattern. Analog builds buttons manually in base oscillator and uses a raw `QButtonGroup`; Digital builds a **ModeButtonGroup** (reusable widget with built-in QButtonGroup). Two different code paths for the same concept.

---

## 2) LFO (wave shape selection)

| Aspect | Analog LFO | Digital LFO |
|--------|------------|-------------|
| **Spec type** | `WaveShapeSpec(shape=W.LFO.*, icon=...)` | Same (inherited from BaseLFOSection) |
| **Spec source** | `BaseLFOSection.generate_wave_shapes()` (same for all LFOs; uses `self.SYNTH_SPEC.Wave.LFO` → Analog.LFO) | Same; `SYNTH_SPEC = Digital` so `W.LFO` = Digital.LFO |
| **When specs set** | After `super().__init__` in `BaseLFOSection`: `self.wave_shapes = self.generate_wave_shapes()` | Same |
| **Who creates buttons** | `SectionBaseWidget._create_shape_row()` (called from `BaseLFOSection._setup_ui()`): builds row with "Shape" label + one button per `wave_shapes`, adds to `wave_shape_group` (QButtonGroup), stores in `wave_shape_buttons[wave.shape]` | Same |
| **Exclusivity** | `wave_shape_group = QButtonGroup(self); wave_shape_group.setExclusive(True)` | Same |
| **Init/layout flow** | `BaseLFOSection`: `SKIP_BASE_SETUP_UI = True` → base does **not** run default `_setup_ui()`. After `super().__init__()`, base calls `self._setup_ui()` which: `create_layout()` → `_build_digital_layout(layout)` or `_build_analog_layout(layout)` → both call `layout.addLayout(self._create_shape_row())` | Same (Digital and Analog LFO share BaseLFOSection) |
| **Stored refs** | `wave_shape_buttons` (shape→btn), `wave_shape_group`; Analog also does `lfo_shape_buttons.update({shape.value: btn ...})` for editor | `wave_shape_buttons` (shape→btn), `wave_shape_group` |

**Summary (LFO):** Fully unified. Analog LFO and Digital LFO (and Mod LFO) all go through **BaseLFOSection** → **`_setup_ui()`** → **`_create_shape_row()`** with **WaveShapeSpec** and a single **QButtonGroup**. One flow, one place.

---

## 3) Mod LFO (wave shape selection)

| Aspect | Digital Mod LFO |
|--------|------------------|
| **Spec type** | Same as LFO: `WaveShapeSpec(shape=W.LFO.*, icon=...)` |
| **Spec source** | `BaseLFOSection.generate_wave_shapes()`; subclass sets `SYNTH_SPEC = Digital` so same Digital LFO shapes |
| **Who creates buttons** | Same: `_create_shape_row()` in BaseLFOSection._setup_ui() |
| **Init/layout flow** | Same as Digital LFO (BaseLFOSection); only difference is `_build_layout_spec()` override for MOD_LFO_* params (rate/depths), not shape row |
| **Stored refs** | Same: `wave_shape_buttons`, `wave_shape_group` |

**Summary (Mod LFO):** Same unified flow as LFO; only layout spec (which sliders/switches) differs.

---

## Cross-cutting comparison

| Topic | Oscillator | LFO / Mod LFO |
|-------|------------|----------------|
| **Spec type** | `SliderSpec` (param, label, icon_name) | `WaveShapeSpec` (shape, icon) with `.param` alias |
| **Unified flow?** | No: Analog = base custom _create_waveform_buttons; Digital = ModeButtonGroup | Yes: all use BaseLFOSection → _create_shape_row() |
| **Exclusivity** | Both use QButtonGroup (Analog in base, Digital inside ModeButtonGroup) | All use same QButtonGroup in _create_shape_row() |
| **Base section flag** | Oscillator does **not** use SKIP_BASE_SETUP_UI | LFO uses SKIP_BASE_SETUP_UI and builds layout in _setup_ui() |

---

## Recommendations for harmonization

1. **LFO / Mod LFO**  
   Already harmonized; no change needed.

2. **Oscillator – use one button-row pattern**  
   - **Option A (recommended):** Use **ModeButtonGroup** for Analog oscillator as well. In `AnalogOscillatorSection` (or base), build a `ModeButtonSpec` list from `wave_shapes` (e.g. `mode=spec.param`, `label=spec.label`, `icon_name=spec.icon_name`) and create a `ModeButtonGroup` with an icon factory that calls `generate_icon_from_waveform(icon_name)`. Add that widget to the layout instead of the current manual row. Then both Analog and Digital oscillator use the same “mode row” abstraction and a single code path for exclusivity and styling.
   - **Option B:** Have Digital oscillator stop using ModeButtonGroup and use the same `BaseOscillatorSection._create_waveform_buttons()` path as Analog (so one implementation in base). Digital would then need to supply wave_shapes in the same SliderSpec form and not use ModeButtonGroup for the wave row.

3. **Shared “shape row” helper (optional)**  
   If desired, introduce a small helper (e.g. `create_mode_row(specs, param_enum, send_midi_cb, analog)`) that:
   - Takes a list of specs (either SliderSpec-like or WaveShapeSpec-like with a common `.param`/`.value` and label/icon),
   - Builds a QButtonGroup + row of buttons,
   - Connects idToggled → send MIDI + optional callback.  
   Oscillator and LFO could both call this with their own spec types and param enums, so layout and exclusivity logic live in one place while specs stay per-domain.

4. **Spec type alignment (optional)**  
   For maximum consistency, oscillator could use a spec type that has the same shape as LFO (e.g. a shared “ModeSpec” with `mode`/`param`, `label`, `icon`), with LFO continuing to use `WaveShapeSpec` that implements that shape. This is optional and mostly for readability and future reuse.

Implementing **Option A** (Analog oscillator uses ModeButtonGroup) would harmonize the oscillator flow with Digital and with the LFO pattern (one reusable component for exclusive mode/shape rows).
