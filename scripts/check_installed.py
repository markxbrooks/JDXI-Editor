"""
Check an installed jdxi_manager package (run from outside the repository).

    python scripts/check_installed.py

Fails (exit 1) when:
- jdxi_editor is imported from a source checkout rather than site-packages
- the resources are not found inside the installed package
- the main window does not open (it is shown offscreen for a moment)

Used by CI on the built wheel, and handy before uploading a release by hand.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

REQUIRED_RESOURCES = (
    "resources/jdxi_icon.png",
    "resources/splash_screen_540_850v5.png",
    "resources/fonts",
    "resources/digital_synths",
    "resources/drum_kits",
)


def main() -> int:
    import jdxi_editor
    from jdxi_editor.project import __version__
    from jdxi_editor.resources import resource_path

    package = Path(jdxi_editor.__file__).resolve().parent
    print(f"jdxi_editor {__version__} from {package}")
    if "site-packages" not in package.parts and "dist-packages" not in package.parts:
        print("FAIL: not an installed package (run from outside the repository)")
        return 1

    missing = [r for r in REQUIRED_RESOURCES if not os.path.exists(resource_path(r))]
    if missing:
        print(f"FAIL: resources missing: {missing}")
        return 1
    if not Path(resource_path("resources")).resolve().is_relative_to(package):
        print(f"FAIL: resources found outside the package: {resource_path('resources')}")
        return 1
    print("resources: inside the package")

    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv[:1])
    from jdxi_editor.ui.windows.jdxi.instrument import JDXiInstrument

    window = JDXiInstrument()
    window.show()
    for _ in range(30):
        app.processEvents()
    window.close()
    print("main window: opened")
    return 0


if __name__ == "__main__":
    sys.exit(main())
