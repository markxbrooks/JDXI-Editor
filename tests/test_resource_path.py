"""Tests for bundled resource path resolution."""

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, os.path.abspath("."))

from jdxi_editor import resources


class TestResourcePath(unittest.TestCase):
    """Ensure resource_path finds assets in dev tree and macOS app bundles."""

    def test_dev_tree_resolves_project_resources(self):
        path = resources.resource_path("resources/splash_screen_540_850v5.png")
        self.assertTrue(os.path.isabs(path))
        self.assertTrue(
            path.endswith(os.path.join("resources", "splash_screen_540_850v5.png"))
        )
        self.assertTrue(os.path.isfile(path), f"missing splash asset: {path}")

    def test_macos_app_bundle_uses_contents_resources(self):
        app_root = Path(__file__).resolve().parent.parent
        fake_exe = app_root / "dist/JD-Xi Editor.app/Contents/MacOS/JD-Xi Editor"
        if not fake_exe.is_file():
            self.skipTest("built .app not present")

        expected = (
            app_root
            / "dist/JD-Xi Editor.app/Contents/Resources/resources/splash_screen_540_850v5.png"
        )
        self.assertTrue(expected.is_file(), "splash PNG not bundled in .app")

        with mock.patch.object(sys, "executable", str(fake_exe)):
            bundle_resources = resources._macos_app_resources_dir()
            self.assertIsNotNone(bundle_resources)
            self.assertEqual(
                bundle_resources,
                fake_exe.resolve().parent.parent / "Resources",
            )

            resolved = resources.resource_path("resources/splash_screen_540_850v5.png")
            self.assertEqual(Path(resolved), expected)

    def test_pyinstaller_meipass_takes_precedence(self):
        with mock.patch.object(sys, "_MEIPASS", "/tmp/fake_meipass", create=True):
            with mock.patch.object(
                resources, "_macos_app_resources_dir", return_value=None
            ):
                resolved = resources.resource_path("resources/foo.png")
                self.assertEqual(resolved, os.path.join("/tmp/fake_meipass", "resources/foo.png"))


if __name__ == "__main__":
    unittest.main()
