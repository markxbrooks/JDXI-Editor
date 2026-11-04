#!/usr/bin/env python3
"""
Unit tests for PicoUI splash screen specs and builders.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication, QGroupBox, QLabel, QProgressBar, QWidget

from picoui.helpers.layout import create_progress_bar_from_spec
from picoui.specs.widgets import (
    GroupBoxSpec,
    LabelSpec,
    LogoSpec,
    ProgressBarSpec,
)
from picoui.splash.config import SplashScreenConfig, group_spec_from_config
from picoui.splash.panel import build_splash_panel
from picoui.splash.screen import SplashScreen
from picoui.widget.helper import (
    create_group_box_from_spec,
    create_label_from_spec,
    create_logo_label_from_spec,
)


def get_qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestProgressBarFromSpec(unittest.TestCase):
  def setUp(self) -> None:
      get_qapp()

  def test_create_progress_bar_from_spec_returns_bar(self) -> None:
      spec = ProgressBarSpec(
          range_min=0,
          range_max=50,
          start_value=5,
          height=18,
          format_text="ElMo",
      )
      bar = create_progress_bar_from_spec(spec)
      self.assertIsInstance(bar, QProgressBar)
      self.assertEqual(bar.minimum(), 0)
      self.assertEqual(bar.maximum(), 50)
      self.assertEqual(bar.value(), 5)
      self.assertIn("ElMo", bar.format())


class TestLogoLabelFromSpec(unittest.TestCase):
  def setUp(self) -> None:
      get_qapp()

  def test_missing_path_yields_empty_label(self) -> None:
      label = create_logo_label_from_spec(LogoSpec())
      self.assertIsInstance(label, QLabel)
      self.assertTrue(label.pixmap() is None or label.pixmap().isNull())

  def test_temp_png_sets_pixmap(self) -> None:
      image = QImage(32, 16, QImage.Format.Format_RGB32)
      image.fill(Qt.GlobalColor.red)
      with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
          path = tmp.name
      try:
          QPixmap.fromImage(image).save(path)
          label = create_logo_label_from_spec(LogoSpec(path=path))
          pixmap = label.pixmap()
          self.assertIsNotNone(pixmap)
          self.assertFalse(pixmap.isNull())
      finally:
          Path(path).unlink(missing_ok=True)


class TestGroupBoxFromSpec(unittest.TestCase):
  def setUp(self) -> None:
      get_qapp()

  def test_create_group_box_from_spec(self) -> None:
      spec = GroupBoxSpec(title="ElMo", foreground_color="white")
      group, layout = create_group_box_from_spec(spec)
      self.assertIsInstance(group, QGroupBox)
      self.assertEqual(group.title(), "ElMo")
      self.assertIsNotNone(layout)


class TestSplashScreenConfig(unittest.TestCase):
  def test_from_title_builds_logo_and_group_defaults(self) -> None:
      config = SplashScreenConfig.from_title(
          title="ElMo",
          logo=LogoSpec(path="/tmp/logo.png"),
          progress=ProgressBarSpec(format_text="loading"),
      )
      self.assertEqual(config.title, "ElMo")
      self.assertEqual(config.logo.path, "/tmp/logo.png")
      self.assertEqual(config.progress.format_text, "loading")
      group = group_spec_from_config(config)
      self.assertEqual(group.title, "ElMo")

  def test_from_title_maps_legacy_style_to_background(self) -> None:
      config = SplashScreenConfig.from_title(
          title="ElMo",
          style="background-color: white;",
      )
      self.assertEqual(config.background_color, "white")

  def test_from_title_legacy_logo_path(self) -> None:
      config = SplashScreenConfig.from_title(
          title="ElMo",
          logo_path="/tmp/legacy.png",
      )
      self.assertEqual(config.logo.path, "/tmp/legacy.png")


class TestLabelFromSpec(unittest.TestCase):
  def setUp(self) -> None:
      get_qapp()

  def test_object_name_applied(self) -> None:
      label = create_label_from_spec(
          LabelSpec(label="Status", object_name="StatusLabel")
      )
      self.assertEqual(label.objectName(), "StatusLabel")


class TestSplashPanel(unittest.TestCase):
  def setUp(self) -> None:
      get_qapp()

  def test_build_jdxi_splash_panel_uses_specs(self) -> None:
      config = SplashScreenConfig.from_title(
          title="ElMo",
          subtitle=LabelSpec(label="Subtitle"),
          status_text="Loading",
          credits_text="v1.0",
      )
      host = QWidget()
      panel = build_splash_panel(host, config)
      self.assertEqual(panel.card.objectName(), "Card")
      self.assertEqual(panel.title_label.objectName(), "TitleLabel")
      self.assertEqual(panel.title_label.text(), "ElMo")
      self.assertIsNotNone(panel.progress_bar)
      self.assertEqual(panel.status_label.objectName(), "StatusLabel")
      self.assertEqual(panel.status_label.text(), "Loading")

  def test_build_jdxi_splash_panel_without_progress(self) -> None:
      config = SplashScreenConfig.from_title(title="About", show_progress=False)
      host = QWidget()
      panel = build_splash_panel(
          host, config, show_progress=False, show_status=False
      )
      self.assertIsNone(panel.progress_bar)
      self.assertIsNone(panel.status_label)


class TestSplashScreenWidget(unittest.TestCase):
  def setUp(self) -> None:
      get_qapp()

  def test_builds_with_progress_bar(self) -> None:
      config = SplashScreenConfig.from_title(title="Test")
      splash = SplashScreen(config)
      self.assertIsNotNone(splash.progress_bar)

  def test_builds_without_progress_bar(self) -> None:
      config = SplashScreenConfig.from_title(title="Test", show_progress=False)
      splash = SplashScreen(config)
      self.assertIsNone(splash.progress_bar)

  def test_subtitle_style_applied(self) -> None:
      config = SplashScreenConfig.from_title(
          title="ElMo",
          subtitle=LabelSpec(label="Subtitle", alignment=Qt.AlignmentFlag.AlignCenter),
      )
      splash = SplashScreen(config)
      self.assertEqual(splash.width(), config.dimensions.width)


if __name__ == "__main__":
    unittest.main()
