# JDXi Manager vs JDXi Editor: Feature Gap Analysis

**Question:** Where does JDXi Manager (Perl 0.30 alpha) provide a stronger workflow or capability than JDXi Editor (Python 0.9.6)?

**Scope:** This comparison is based on the Manager source in `/Users/brooks/projects/jdxi_manager-030` and Editor source and documentation in this repository. It compares implemented workflows, not aspirational Sphinx prose. “Stronger” means a capability is more direct, explicit, or complete in Manager; it does not mean Manager is the broader application.

## Summary

JDXi Manager’s clearest advantages are its direct hardware round-trip workflow for each sound section, its integrated factory-preset browsing/loading, and its convenient per-section SysEx librarian flow. It also has a couple of small hands-on editing features: random analog tone generation and copy/paste of a synth or drum partial.

JDXi Editor is substantially broader overall: it includes a pattern sequencer, MIDI file player, SoundFont playback, searchable preset selection, and a richer patch bundle workflow. The comparison below isolates Manager’s advantages.

## Manager advantages

| Area | What Manager does better | Evidence in Manager | Editor comparison | Priority |
|---|---|---|---|---|
| **Read current hardware data on demand** | Every relevant editor exposes **Read from** and **Dump to**. Read issues RQ1 requests, receives and validates DT1 data, then populates the editor state. This is a clear, user-invoked hardware-to-editor round trip. | `jdxi_manager.pl`: `EditBufferOps`, `SysexPatRcve`, `SyxReceive` | Editor requests data when editors are shown and handles incoming SysEx, but its documented patch save flow saves current UI values and has no explicit “Read from synth, then save” operation. | **High** |
| **Factory preset selection inside the part editor** | Analog, Digital 1/2, and Drum editors include a populated preset list, wheel-based previous/next selection, and a Load button that selects the hardware preset and then reads its data into the editor. | `jdxi_manager.pl`: `EditBufferOps`, `LoadPreset`, `ChgPreset`; factory lists in `JDXidata.pm` | Editor has preset selection and search, but the Manager’s integrated “select hardware preset → load → inspect/edit its parameters” flow is a particularly direct browsing experience. | **Medium** |
| **Per-section SysEx librarian workflow** | Each editor can open/save its own patch file, retain the selected filename for Save, and browse a folder of patch files. Manager also validates section lengths and parameter patterns when loading. | `jdxi_manager.pl`: `FileMenu`, `browseFile`, `loadFile`, `saveFile`, `saveasFile`, `saveSub`, `ValidatePatData` | Editor supports `.syx` plus JSON and bundled `.jsz`/`.msz`; its bundle saves multiple sections together. Manager’s advantage is the focused, per-part file workflow and explicit validation. | **Medium** |
| **Random analog tone generation** | The Analog editor has a dedicated random tone action which creates a randomized analog patch and sends it to the instrument when connected. | `jdxi_manager.pl`: `rndVoice` and Analog editor File menu | No comparable user-facing random analog patch action was found in Editor’s feature list or implementation search. | **Low** |
| **Copy/paste a partial between parts or drum sounds** | Editor menus provide Copy Partial and Paste Partial; paste checks that the source and destination partial data lengths match. | `jdxi_manager.pl`: `FileMenu`, `copyPart`, `pastePart` | No matching partial clipboard operation was found in Editor’s documented workflows or source search. | **Low** |

## Recommended gaps to close

1. **Add a “Read from JD-Xi” action to patch management.** Request all supported sections, wait for and validate responses, update the editor state, then allow saving. Show which sections were successfully read so a partial response cannot silently look complete.
2. **Make factory preset auditioning a first-class workflow.** In the part editor, keep preset selection, hardware load, and readback together; add previous/next navigation if that is not already available in the current UI.
3. **Offer optional per-part SysEx import/export.** Keep the existing multi-section JSON bundle flow, while allowing a user to load or save one compatible part file. Validate the target address and data length before sending.
4. **Add partial copy/paste and an analog randomizer** as small editing conveniences, if they fit the current editor interaction model.

## Important caveats

- Both applications’ documented save flows use editor/UI state as the saved source. Manager’s **Read from** action improves the workflow by letting users refresh that state first; it is not an automatic hardware dump-to-file operation.
- Manager’s `.syx` workflow is per editor/part. Editor’s `.jsz`/`.msz` formats are more convenient for saving a broader working set, and Editor also supports MIDI, patterns, and software playback features that are outside Manager’s scope.
- “No comparable feature found” means no matching implemented workflow was found during this source/document review; it is not a claim that no code path could be adapted to provide it.

## Source references

- Manager UI and actions: `/Users/brooks/projects/jdxi_manager-030/jdxi_manager.pl` (`EditBufferOps`, `LoadPreset`, `rndVoice`, `browseFile`, `loadFile`, `saveSub`, `copyPart`, `pastePart`, `SysexPatRcve`, `SyxReceive`).
- Manager preset tables and patch data: `/Users/brooks/projects/jdxi_manager-030/JDXidata.pm`.
- Editor patch save/load comparison and readback limitation: [`patch-saving-gap-analysis.md`](patch-saving-gap-analysis.md).
- Editor overview and feature scope: [`features-and-usage.md`](features-and-usage.md).
