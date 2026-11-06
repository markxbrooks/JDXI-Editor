"""
The MIDI layer (jdxi_editor.midi) must not depend on the UI layer.

The UI may import the MIDI layer, never the other way round, so the MIDI and
SysEx code can be tested and reused without Qt widgets. Imports inside
functions and under TYPE_CHECKING are not counted.

ALLOWED lists the module-level imports that remain; remove entries as they
are fixed, never add to it.
"""

import ast
from pathlib import Path

import pytest

MIDI_ROOT = Path(__file__).resolve().parent.parent / "jdxi_editor" / "midi"

ALLOWED = {
    # midi module (relative to jdxi_editor/midi) -> ui modules it imports
    "data/effects/sysex/dispatcher.py": {
        "jdxi_editor.ui.widgets.controls.registry",
        "jdxi_editor.ui.widgets.writer",
    },
    "data/effects/type/router.py": {"jdxi_editor.ui.widgets.writer"},
    "data/parameter/analog/spec.py": {"jdxi_editor.ui.style"},
    "data/parameter/digital/spec.py": {"jdxi_editor.ui.style"},
    "io/controller.py": {"jdxi_editor.ui.windows.jdxi.helpers.port"},
    "io/helper.py": {"jdxi_editor.ui.windows.jdxi.helpers.port"},
    "io/input_handler.py": {
        "jdxi_editor.ui.preset.button",
        "jdxi_editor.ui.preset.incoming_data",
        "jdxi_editor.ui.programs",
    },
    "program/helper.py": {"jdxi_editor.ui.editors.helpers.program"},
    "program/program.py": {"jdxi_editor.ui.preset.data"},
    "utils/helpers.py": {"jdxi_editor.ui.windows.jdxi.utils"},
    "validation/selection.py": {"jdxi_editor.ui.midi.selection_info"},
}


def _is_type_checking(node: ast.If) -> bool:
    test = node.test
    return (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or (
        isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"
    )


def _module_level_ui_imports(path: Path) -> set[str]:
    found = set()

    def visit(nodes):
        for node in nodes:
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith(
                "jdxi_editor.ui"
            ):
                found.add(node.module)
            elif isinstance(node, ast.Import):
                found.update(
                    a.name for a in node.names if a.name.startswith("jdxi_editor.ui")
                )
            elif isinstance(node, ast.If) and not _is_type_checking(node):
                visit(node.body)
                visit(node.orelse)
            elif isinstance(node, ast.Try):
                visit(node.body)
                for handler in node.handlers:
                    visit(handler.body)
                visit(node.orelse)
                visit(node.finalbody)

    visit(ast.parse(path.read_text(encoding="utf-8")).body)
    return found


def _actual() -> dict[str, set[str]]:
    actual = {}
    for path in sorted(MIDI_ROOT.rglob("*.py")):
        imports = _module_level_ui_imports(path)
        if imports:
            actual[path.relative_to(MIDI_ROOT).as_posix()] = imports
    return actual


def test_no_new_ui_imports_in_midi_layer():
    new = {
        module: sorted(imports - ALLOWED.get(module, set()))
        for module, imports in _actual().items()
        if imports - ALLOWED.get(module, set())
    }
    assert new == {}, "jdxi_editor.midi must not import jdxi_editor.ui"


def test_allowlist_has_no_fixed_entries():
    """Fixed imports are removed from ALLOWED, so it only shrinks."""
    actual = _actual()
    stale = {
        module: sorted(imports - actual.get(module, set()))
        for module, imports in ALLOWED.items()
        if imports - actual.get(module, set())
    }
    assert stale == {}
