# Translations (i18n)

The app uses **Qt Linguist** for translations. Strings are marked with `self.tr("...")` in code; at runtime the correct translation is chosen from `.qm` files based on the system locale.

## Quick example: UK English ("Bar" instead of "Measure")

1. **Extract translatable strings** (from project root):
   ```bash
   pylupdate6 jdxi_editor/ui/editors/pattern/pattern.py jdxi_editor/main.py -ts jdxi_editor/i18n/jdxi_editor_en_GB.ts
   ```
   Or use `lupdate` on the whole project if you use a `.pro` file.

2. **Edit the .ts file** in Qt Linguist or by hand. For UK English, set:
   - `Measure` → `Bar`
   - `Measures` → `Bars`
   - `Copy previous measure` → `Copy previous bar`

3. **Compile to .qm**:
   ```bash
   lrelease jdxi_editor/i18n/jdxi_editor_en_GB.ts -qm jdxi_editor/i18n/jdxi_editor_en_GB.qm
   ```

4. **Run with UK locale** (so the app loads `en_GB`):
   - macOS/Linux: `LANG=en_GB.UTF-8 python -m jdxi_editor.main` (or set in System Preferences / regional settings)
   - Or the app will use the OS locale automatically if it matches a loaded translation.

The app looks for `.qm` files in:

- `jdxi_editor/i18n/jdxi_editor_<locale>.qm` (e.g. `jdxi_editor_en_GB.qm`)
- `jdxi_editor/resources/translations/`
- project root `i18n/`
