#!/usr/bin/env python3
"""Help → Documentation opens the local Sphinx build if there is one,
otherwise the published docs (app bundles don't include the build)."""

import os
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from jdxi_editor.ui.windows.jdxi import instrument


def _open_docs(index_exists: bool, tmp_path):
    index = tmp_path / "index.html"
    if index_exists:
        index.write_text("<html></html>")
    with patch.object(
        instrument, "documentation_file_path", return_value=str(index)
    ), patch.object(instrument, "os_file_open") as file_open, patch.object(
        instrument.webbrowser, "open"
    ) as browser_open:
        instrument.JDXiInstrument.on_documentation(SimpleNamespace())
    return file_open, browser_open, index


def test_missing_local_build_opens_the_published_docs(tmp_path):
    file_open, browser_open, _ = _open_docs(False, tmp_path)
    file_open.assert_not_called()
    browser_open.assert_called_once_with(instrument.DOCUMENTATION_URL)


def test_local_build_is_preferred(tmp_path):
    file_open, browser_open, index = _open_docs(True, tmp_path)
    file_open.assert_called_once_with(str(index))
    browser_open.assert_not_called()
