# PicoMIDI Project Restructuring — Migration Plan

This document describes the recommended migration steps for restructuring the PicoMIDI project into a clearer and more maintainable package layout.

---

## 1. New Package Structure

Create the following structure:

```
picomidi/
  messages/
    __init__.py
    note.py
    control_change.py
    program_change.py
    pitch_bend.py
    aftertouch.py
    song.py
    sysex.py

  core/
    __init__.py
    channel.py
    value.py
    tempo.py
    utils.py
```

---

## 2. File Moves (`git mv` Recommended)

Run these moves rather than deleting and recreating files so history is preserved.

```
git mv picomidi/note.py picomidi/messages/note.py
git mv picomidi/song.py picomidi/messages/song.py
git mv picomidi/value.py picomidi/core/value.py
git mv picomidi/tempo.py picomidi/core/tempo.py
git mv picomidi/channel.py picomidi/core/channel.py

git mv picomidi/cc/control_change.py picomidi/messages/control_change.py
git mv picomidi/pc/program_change.py picomidi/messages/program_change.py
git mv picomidi/pitch/bend.py picomidi/messages/pitch_bend.py
git mv picomidi/sysex/byte.py picomidi/messages/sysex.py
```

Remove now-empty directories after validation.

---

## 3. Introduce New Public API (`picomidi/__init__.py`)

Expose the curated surface:

```python
from .messages import (
    Note,
    ControlChange,
    ProgramChange,
    PitchBend,
    Aftertouch,
    SongMessage,
    SysExMessage,
)

from .core import MidiChannel, MidiValue, MidiTempo
```

This allows consumer imports such as:

```python
from picomidi import ControlChange, PitchBend
```

---

## 4. Provide Backward-Compatibility Shims (Temporary)

Add compatibility imports to old module paths to avoid breaking users immediately.

Example (`picomidi/cc/__init__.py`):

```python
from picomidi.messages.control_change import ControlChange
__all__ = ["ControlChange"]
```

Repeat for:

- `cc`
- `pc`
- `pitch`
- `sysex`

---

## 5. Deprecation Notices

Inside compatibility shims, add warnings:

```python
import warnings
warnings.warn(
    "picomidi.cc.control_change is deprecated; "
    "use picomidi.messages.control_change instead.",
    DeprecationWarning,
    stacklevel=2,
)
```

Plan to remove these in a future major release.

---

## 6. Update Internal Imports

Search and replace across the codebase:

- `from picomidi.cc.control_change` → `from picomidi.messages.control_change`
- `from picomidi.pitch.bend` → `from picomidi.messages.pitch_bend`
- `from picomidi.pc.program_change` → `from picomidi.messages.program_change`
- `from picomidi.sysex.byte` → `from picomidi.messages.sysex`
- `from picomidi.value` → `from picomidi.core.value`
- `from picomidi.channel` → `from picomidi.core.channel`

Run tests after each stage.

---

## 7. Documentation and Examples Update

Update:

- README import examples
- usage docs
- tutorial code snippets
- inline docstrings

Ensure all examples use the new top-level API.

---

## 8. Release Strategy

1. **vNext Minor Release**
   - New structure
   - Backward-compat shims
   - Deprecation warnings

2. **Future Major Release**
   - Remove deprecated paths
   - Announce in changelog

---

## 9. Validation Checklist

- [ ] Tests green
- [ ] Old imports still function (with warnings)
- [ ] New import API works everywhere
- [ ] Docs updated
- [ ] Changelog entry added

---

## 10. Optional Enhancements

- Introduce `MidiMessage` base protocol for polymorphic handling
- Add `messages/__all__` export control
- Add type coverage (`mypy --strict`)
- Provide auto-formatter for message encoding/decoding

---

## Outcome

This migration:

- simplifies navigation
- aligns modules with MIDI semantics
- preserves public API stability
- supports future extensibility

