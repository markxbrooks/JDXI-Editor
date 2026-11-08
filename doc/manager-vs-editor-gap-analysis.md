# JDXi Manager vs JDXi Editor: Updated Feature Gap Analysis

**Question:** Where does JDXi Manager (Perl 0.30 alpha) currently provide a stronger feature than JDXi Editor?

**Review date:** 2026-11-04. This revision rechecks the current Editor implementation, including the current workspace changes, against Manager source. It focuses on implemented capabilities rather than aspirational documentation.

## Summary

The earlier analysis was stale. Editor has since added Manager-style hardware readback, preset navigation and loading, per-editor SysEx import/export, analog randomization, and partial copy/paste. Those are no longer Manager advantages.

The clearest remaining Manager advantage is **stricter validation of incoming SysEx dumps**: Manager checks exact expected section length, section-specific data patterns, and Roland checksum before accepting the dump into its editor state. Editor's per-part import currently checks that messages exist and performs a part address-area check, then sends the messages; it does not verify each message's expected length, data pattern, or checksum in this import path.

## Current comparison

| Capability | JDXi Manager | JDXi Editor | Assessment |
|---|---|---|---|
| Read current hardware data | Per-editor **Read from** / RQ1 flow | Per-editor Read from controls; Patch Manager also has **Read from JD-Xi** and **Read then Save**, with section status | At parity; Editor has a broader all-sections save flow |
| Select and load factory presets | Preset list and Load in the part editor | Searchable selection plus previous/next and Load | At parity; Editor offers search |
| Per-part SysEx files | Per-editor open/save, with stored filename and folder browser | Per-editor Import/Export `.syx`; validates area and refreshes after import | At parity for normal workflow; Manager has stronger dump validation |
| Random analog tone | Random analog patch action | **Random Patch** action in Analog preset UI | At parity |
| Copy/paste partials | Copy/paste partial operations | Copy/paste in Digital and Drum editors | At parity |
| Incoming SysEx dump validation | Exact message length, section pattern, and checksum validation | Per-part import validates that messages are present and checks expected address area, but does not currently check per-message expected length/pattern/checksum | **Manager ahead** |
| Legacy file variants | Supports editor-specific `.as`, `.ds`, `.dk` ASCII-hex import paths (where enabled), in addition to `.syx` | General `.syx`, `.json`, `.jsz`, `.msz`; no matching `.as`/`.ds`/`.dk` import was found | **Manager ahead** for compatibility with those legacy files |

## Remaining gaps to close

1. **Validate each imported SysEx message before sending.** For the target editor, verify manufacturer/model/command, expected address and section size, legal data bytes, and checksum. Report the exact failing section and reject the file before sending any messages.
2. **Consider legacy ASCII-hex formats only if there are users or archives that need them.** Manager's `.as`, `.ds`, and `.dk` handling is a niche compatibility advantage; the current `.syx` and bundled formats are more general for new workflows.

## Evidence and limits

- Manager's `ValidatePatData` in `/Users/brooks/projects/jdxi_manager-030/jdxi_manager.pl` checks expected length, a section-specific regular-expression pattern, and checksum. Both file loading and hardware receive call it before accepting data.
- Editor's `validate_part_syx` in `jdxi_editor/midi/sysex/part_syx.py` splits F0…F7 blocks and checks the expected address area. `import_syx_to_editor` then sends each message and requests a refresh. It currently does not perform the same length/pattern/checksum validation.
- Editor's updated feature implementation is in `jdxi_editor/ui/editors/helpers/edit_buffer_ops.py`, `jdxi_editor/ui/preset/widget.py`, `jdxi_editor/ui/editors/analog/editor.py`, `jdxi_editor/ui/editors/digital/editor.py`, and `jdxi_editor/ui/editors/drum/editor.py`.
- Manager code reviewed: `/Users/brooks/projects/jdxi_manager-030/jdxi_manager.pl` and `/Users/brooks/projects/jdxi_manager-030/JDXidata.pm`.
- This is a source-level comparison. It does not claim runtime testing of either app or hardware.
