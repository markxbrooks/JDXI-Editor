# JD-Xi Studio v2 features: what to reimplement

JD-Xi Studio builds these features on its v2 interface (`jdxi_editor/ui/v2/`),
which the Editor does not have. They were not ported with the rest of the
Studio work on `port/jdxi-studio`. This note records, for each one, what it
needs and whether it is worth reimplementing on the Editor's own editors.

Sizes are lines in Studio. "Needs" lists the v2 modules the feature imports.

| Feature | Studio module | Lines | Needs | Decision |
|---|---|---|---|---|
| Undo / redo / reload | `history.py` | 587 | nothing | Done: Digital, Analog, Drum |
| SuperNATURAL partial tools | `partial_tools.py` | 271 | nothing | Reimplement, after undo |
| PCM wave browser | `wave_browser.py` | 320 | nothing | Reimplement, after undo |
| Randomize a tone | `randomize_dialog.py` | 126 | nothing | Reimplement, after undo |
| A/B compare | `ab_compare.py` | 1003 | context, framework, history, partial_tools | Reimplement later |
| Save on the JD-Xi wizard | `write_wizard.py` | 388 | context, safety_net | Reimplement later, tested on the instrument |
| Self-test window | `windows/selftest.py` | 885 | history | Leave out; reconsider after undo |
| Programs page with mixer | `programs.py` | 1118 | brand, context, history, offline, restyle, widgets, write_wizard | Leave out |
| Recipes | `recipes.py` | 1936 | context, history, restyle, widgets | Leave out for now |
| Italian translation | `i18n/` | 2069 strings | `tr()` at 1928 call sites | Leave out for now |

## Reimplement

**Undo / redo / reload.** Done, in `jdxi_editor/ui/editors/history.py`, on the
Digital, Analog and Drum editors. A change is recorded where a control sends a
parameter. A value applied with the control's signals blocked came from the
JD-Xi and is not a step. A drag of one slider is one step. Reload puts back
every value as it was before its first change. A program change clears the
steps, because the sound they belong to has been replaced. Studio's warning
before a new sound discards edits is not part of this: the Editor still
replaces the sound, and the steps are cleared. The wave browser, randomize and
partial tools can each make one step through `begin_group` / `end_group`.

**SuperNATURAL partial tools, the PCM wave browser and randomize.** None of
them imports v2. They work on the three partials of a Digital tone:

- link partials (a change goes to the other partials that are on, except the
  oscillator's identity), and copy, paste and swap a partial or a section;
- the 160 PCM waves by family, with search, favourites and "Try", which sets
  the wave and plays a short note;
- randomize a section, a partial or the whole tone by a small, medium or
  large amount.

The Editor already has a PCM wave control (`ui/widgets/pcm/wave.py`) and an
Analog randomize (`ui/editors/helpers/analog_random.py`); the Studio versions
add the Digital side. Each should follow undo, so that one press is one step.

**A/B compare.** Two snapshots of one part's tone, switched while playing.
It is the largest of the editing features and depends on v2's context and
framework. Reimplement it after undo, on the Editor's Digital and Analog
editors, with the snapshot taken from the editor's own parameter values.

**Save on the JD-Xi wizard.** The JD-Xi only writes whole programs into banks
E–H. The wizard names the temporary program, chooses a slot from the user
program names the Editor knows, guides the WRITE on the instrument and checks
it by reading the slot back. It is worth having, but every step talks to the
instrument, so it needs testing on a JD-Xi (`pytest -m hardware`) before it
ships.

## Leave out

**Self-test window.** It plays the user through the app's own windows (load a
program, choose tones, edit a value and undo it, change the octave, play a
note), checks each result by reading the JD-Xi back or by asking the user, and
saves a Markdown report for bug reports. Its steps call Studio's windows and
undo, so it would be rewritten rather than ported. The Editor's hardware test
suite (`python -m pytest -m hardware`) and `tests/test_jdxi_checks.py` cover
the reads and the connection; the guided report is worth reconsidering once
undo exists.

**Programs page with mixer.** This is v2's page layout around the Editor's
existing program widgets. Porting it would mean porting v2's look (brand,
restyle, widgets), which conflicts with the Editor's skins.

**Recipes.** Step-by-step instructions for making sounds, with a library,
editing and export. It is the largest single module and is content as much as
code. It could come back as documentation (`doc/`) without the workspace.

**Italian translation.** Studio wraps 1928 strings in `tr()` and ships 2069
translated messages. The Editor already loads a `.qm` file at start-up
(`main.py`), but its strings are plain, so the Studio file would not match.
Reimplementing it means wrapping the Editor's strings first; it is worth doing
only with a translator to keep it current.

## Order

1. Undo / redo / reload in the Digital, Analog and Drum editors. Done.
2. Partial tools, the wave browser and randomize for Digital tones.
3. A/B compare.
4. The Save on the JD-Xi wizard, with hardware tests.
