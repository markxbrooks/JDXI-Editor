#!/usr/bin/env python3
"""
Update checks against GitHub Releases: picking the newest published release
with a build for this install, comparing versions, the once-a-day schedule,
and the checker's signals (fed from local files, never the network).
"""

import json
import os
from datetime import datetime, timedelta, timezone

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QSettings, QUrl
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from jdxi_editor.update import checker as upd


def _asset(name):
    return {"name": name, "browser_download_url": f"https://example.invalid/{name}"}


# The shape GitHub returned for this repository (trimmed), plus a draft and a
# pre-release that must be ignored.
RELEASES = [
    {"tag_name": "v1.0.0", "draft": True, "assets": [_asset("x.pkg")]},
    {"tag_name": "v0.9.10-beta", "prerelease": True, "assets": [_asset("x.pkg")]},
    {
        "tag_name": "v0.9.9",
        "name": "JD-Xi Editor v0.9.9",
        "body": "## What's new\n- Things",
        "html_url": "https://github.com/markxbrooks/JDXI-Editor/releases/tag/v0.9.9",
        "assets": [
            _asset("JD-Xi.Editor.app.zip"),
            _asset("JD-Xi_Editor_0.9.9_MacOS_Universal.pkg"),
            _asset("jdxi-editor-0.9.9-x86_64.AppImage"),
            _asset("jdxi-editor_0.9.9_amd64.deb"),
            _asset("jdxi_editor-0.9.9_setup_win_x86-64.exe"),
        ],
    },
    {"tag_name": "v0.9.8", "name": "JD-XI Editor v0.9.8", "assets": []},
    {
        "tag_name": "v0.9.7",
        "assets": [_asset("JD-Xi.Editor.app.zip"), _asset("x_0.9.7.pkg")],
    },
    {"tag_name": "0.9.6", "assets": [_asset("y.exe"), _asset("y.AppImage")]},
]


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def settings(tmp_path):
    return QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)


@pytest.mark.parametrize(
    "text, expected",
    [("v0.9.9", (0, 9, 9)), ("0.9.6", (0, 9, 6)), ("V1.2", (1, 2)), ("x", None)],
)
def test_parse_version(text, expected):
    assert upd.parse_version(text) == expected


@pytest.mark.parametrize(
    "candidate, current, newer",
    [
        ("0.9.10", "0.9.9", True),
        ("v0.9.9", "0.9.9", False),
        ("0.9.8", "0.9.9", False),
        ("1.0", "0.9.9", True),
        ("0.9.9.1", "0.9.9", True),
        ("garbage", "0.9.9", False),
    ],
)
def test_is_newer(candidate, current, newer):
    assert upd.is_newer(candidate, current) is newer


@pytest.mark.parametrize(
    "kind, asset",
    [
        (upd.MACOS, "JD-Xi_Editor_0.9.9_MacOS_Universal.pkg"),
        (upd.WINDOWS, "jdxi_editor-0.9.9_setup_win_x86-64.exe"),
        (upd.APPIMAGE, "jdxi-editor-0.9.9-x86_64.AppImage"),
        (upd.DEB, "jdxi-editor_0.9.9_amd64.deb"),
        (upd.LINUX, "jdxi-editor-0.9.9-x86_64.AppImage"),
    ],
)
def test_newest_published_release_with_a_build(kind, asset):
    release = upd.pick_release(RELEASES, kind)
    assert release.version == "0.9.9"  # not the draft or the pre-release
    assert release.asset_name == asset
    assert release.asset_url.endswith(asset)
    assert release.notes.startswith("## What's new")


def test_release_without_builds_is_skipped():
    # v0.9.8 was published with no builds: offer v0.9.7 to macOS instead
    without_099 = [r for r in RELEASES if r["tag_name"] != "v0.9.9"]
    assert upd.pick_release(without_099, upd.MACOS).version == "0.9.7"
    # the Windows build is only in "0.9.6", a tag without the "v"
    assert upd.pick_release(without_099, upd.WINDOWS).version == "0.9.6"


def test_pip_installs_need_no_build():
    without_099 = [r for r in RELEASES if r["tag_name"] != "v0.9.9"]
    release = upd.pick_release(without_099, upd.PIP)
    assert release.version == "0.9.8" and release.asset_url is None


def test_auto_check_is_on_by_default_and_daily(settings):
    now = datetime(2026, 11, 7, 12, tzinfo=timezone.utc)
    assert upd.should_auto_check(settings, now)  # never checked
    settings.setValue(upd.LAST_CHECK_KEY, (now - timedelta(hours=3)).isoformat())
    assert not upd.should_auto_check(settings, now)
    settings.setValue(upd.LAST_CHECK_KEY, (now - timedelta(days=2)).isoformat())
    assert upd.should_auto_check(settings, now)
    settings.setValue(upd.AUTO_CHECK_KEY, "false")  # as an INI file stores it
    assert not upd.should_auto_check(settings, now)


def _checker(tmp_path, settings, payload, current="0.9.8", kind=upd.MACOS):
    path = tmp_path / "releases.json"
    path.write_text(json.dumps(payload) if payload is not None else "not json")
    checker = upd.UpdateChecker(
        url=QUrl.fromLocalFile(str(path)).toString(),
        current_version=current,
        kind=kind,
        settings=settings,
    )
    results = []
    checker.update_available.connect(lambda r, m: results.append(("update", r, m)))
    checker.up_to_date.connect(lambda v, m: results.append(("current", v, m)))
    checker.failed.connect(lambda e, m: results.append(("failed", e, m)))
    return checker, results


def _run(checker, results, manual):
    checker.check(manual=manual)
    for _ in range(100):
        if results:
            break
        QTest.qWait(20)
    assert not checker.is_checking
    return results


def test_checker_reports_a_newer_release(app, tmp_path, settings):
    checker, results = _checker(tmp_path, settings, RELEASES)
    [(what, release, manual)] = _run(checker, results, manual=False)
    assert (what, release.version, manual) == ("update", "0.9.9", False)
    assert settings.value(upd.LAST_CHECK_KEY)  # recorded for the daily schedule


def test_checker_reports_up_to_date(app, tmp_path, settings):
    checker, results = _checker(tmp_path, settings, RELEASES, current="0.9.9")
    assert _run(checker, results, manual=True) == [("current", "0.9.9", True)]


def test_skipped_version_is_only_offered_on_a_manual_check(app, tmp_path, settings):
    settings.setValue(upd.SKIPPED_VERSION_KEY, "0.9.9")
    checker, results = _checker(tmp_path, settings, RELEASES)
    assert _run(checker, results, manual=False) == [("current", "0.9.9", False)]
    results.clear()
    assert _run(checker, results, manual=True)[0][0] == "update"


@pytest.mark.parametrize(
    "payload, error",
    [
        ({"message": "API rate limit exceeded"}, "API rate limit exceeded"),
        (None, "Unexpected reply from GitHub"),
    ],
)
def test_checker_reports_bad_replies(app, tmp_path, settings, payload, error):
    checker, results = _checker(tmp_path, settings, payload)
    [(what, message, manual)] = _run(checker, results, manual=True)
    assert what == "failed" and error in message and manual
    assert not settings.value(upd.LAST_CHECK_KEY)  # try again next startup


def test_checker_reports_network_errors(app, tmp_path, settings):
    checker = upd.UpdateChecker(
        url=QUrl.fromLocalFile(str(tmp_path / "missing.json")).toString(),
        settings=settings,
    )
    results = []
    checker.failed.connect(lambda e, m: results.append(e))
    _run(checker, results, manual=False)
    assert results and results[0]


def test_dialog_skip_and_pip_instructions(app, settings):
    from jdxi_editor.ui.dialogs.update import AUTO_CHECK_NOTICE, UpdateDialog
    from PySide6.QtWidgets import QLabel, QPushButton

    release = upd.pick_release(RELEASES, upd.PIP)
    dialog = UpdateDialog(release, upd.PIP, settings=settings, current_version="0.9.8")
    texts = [label.text() for label in dialog.findChildren(QLabel)]
    assert any(upd.PIP_UPGRADE_COMMAND in t for t in texts)
    assert AUTO_CHECK_NOTICE in texts  # says automatic checking is on
    buttons = [b.text() for b in dialog.findChildren(QPushButton)]
    assert "Download" not in buttons  # pip installs upgrade from PyPI
    dialog.on_skip()
    assert settings.value(upd.SKIPPED_VERSION_KEY) == "0.9.9"

    mac = UpdateDialog(upd.pick_release(RELEASES, upd.MACOS), upd.MACOS, settings=settings)
    assert "Download" in [b.text() for b in mac.findChildren(QPushButton)]
