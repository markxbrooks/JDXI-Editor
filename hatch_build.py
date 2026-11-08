"""
Hatch build hook: ship resources/ at a size PyPI accepts.

The PNGs in resources/ are kept at full resolution for editing (up to 4267 px,
about 108 MB), but the editor shows them at 350 x 200 at most. Packages get
copies no larger than MAX_IMAGE_SIZE (enough for a 2x display), which brings
the wheel under PyPI's 100 MB file limit. Image-editor sources and demo
animations are left out.

    wheel: resources/... -> jdxi_editor/_bundle/resources/...  (inside the
           package, so nothing is installed at the top of site-packages;
           jdxi_editor.resources looks there first)
    sdist: resources/... -> resources/...  (building a wheel from it shrinks
           nothing further; the copies are already small)
"""

from __future__ import annotations

import fnmatch
import shutil
import tempfile
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

MAX_IMAGE_SIZE = 900  # px, longest side (the 540 x 850 splash screen is kept as it is)
RESOURCES = "resources"
EXCLUDE = ("*.xcf", "*.rhif", "*.ai", "*.bmp", "*.gif", "*.mp4", "*.mov", ".DS_Store")
WHEEL_PREFIX = "jdxi_editor/_bundle"


def shipped_files(root: Path) -> list[Path]:
    """Files under resources/ that are packaged."""
    return sorted(
        path
        for path in (root / RESOURCES).rglob("*")
        if path.is_file() and not any(fnmatch.fnmatch(path.name, p) for p in EXCLUDE)
    )


def shrink_png(source: Path, target: Path) -> None:
    """Copy *source* to *target*, scaled down to MAX_IMAGE_SIZE if larger."""
    from PIL import Image

    target.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        if max(image.size) <= MAX_IMAGE_SIZE:
            shutil.copy2(source, target)
            return
        image = image.copy()
        image.thumbnail((MAX_IMAGE_SIZE, MAX_IMAGE_SIZE), Image.Resampling.LANCZOS)
        image.save(target, "PNG", optimize=True)


class CustomBuildHook(BuildHookInterface):
    """Add resources/ to the sdist and wheel, with large PNGs scaled down."""

    def initialize(self, version: str, build_data: dict) -> None:
        root = Path(self.root)
        self._staging = Path(tempfile.mkdtemp(prefix="jdxi_resources_"))
        prefix = WHEEL_PREFIX + "/" if self.target_name == "wheel" else ""
        for source in shipped_files(root):
            relative = source.relative_to(root)
            if source.suffix.lower() == ".png":
                staged = self._staging / relative
                shrink_png(source, staged)
            else:
                staged = source
            build_data["force_include"][str(staged)] = prefix + relative.as_posix()

    def finalize(self, version: str, build_data: dict, artifact_path: str) -> None:
        shutil.rmtree(getattr(self, "_staging", ""), ignore_errors=True)
