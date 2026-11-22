#!/usr/bin/env python3
"""
Finding the native FluidSynth library on Windows before ``import fluidsynth``
(pyfluidsynth only searches PATH and C:\\tools\\fluidsynth\\bin), and the
status messages when it is missing.
"""

import os
from pathlib import Path

import pytest

from jdxi_editor.midi import fluidsynth_library as fsl


@pytest.fixture(autouse=True)
def fresh(monkeypatch):
    monkeypatch.setattr(fsl, "_prepared_dir", None)
    monkeypatch.setattr(fsl, "_dll_directory_handles", [])
    monkeypatch.setenv("PATH", "C:\\Windows")


def _dll(folder: Path) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "libfluidsynth-3.dll").write_bytes(b"")
    return folder


def test_first_folder_with_the_dll_wins(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    found = _dll(tmp_path / "second")
    _dll(tmp_path / "third")
    missing = tmp_path / "missing"
    assert fsl.find_library_dir([missing, empty, found, tmp_path / "third"]) == found


def test_chocolatey_layout_is_searched_one_level_down(tmp_path):
    tools = tmp_path / "chocolatey" / "lib" / "fluidsynth" / "tools"
    bin_dir = _dll(tools / "fluidsynth-2.4.4-win10-x64" / "bin")
    assert fsl.find_library_dir([tools]) == bin_dir


def test_nothing_found(tmp_path):
    assert fsl.find_library_dir([tmp_path]) is None


def test_fluidsynth_dir_env_is_searched_first(tmp_path, monkeypatch):
    install = tmp_path / "FluidSynth"
    _dll(install / "bin")
    monkeypatch.setenv(fsl.FLUIDSYNTH_DIR_ENV, str(install))
    dirs = fsl.candidate_dirs()
    assert dirs[:2] == [install, install / "bin"]
    assert fsl.find_library_dir() == install / "bin"


def test_repository_copy_is_a_candidate():
    # fluidsynth/bin with libfluidsynth-3.dll is committed to the repository
    assert fsl._REPOSITORY_ROOT / "fluidsynth" / "bin" in fsl.candidate_dirs()
    assert fsl.find_library_dir([fsl._REPOSITORY_ROOT / "fluidsynth" / "bin"])


def test_prepare_on_windows_puts_the_folder_on_path(tmp_path, monkeypatch):
    folder = _dll(tmp_path / "bin")
    monkeypatch.setattr(fsl, "candidate_dirs", lambda: [folder])
    added = []
    monkeypatch.setattr(os, "add_dll_directory", added.append, raising=False)
    assert fsl.prepare_fluidsynth_library("win32") == folder
    assert os.environ["PATH"].split(os.pathsep)[0] == str(folder)
    assert added == [str(folder)]
    # once only
    assert fsl.prepare_fluidsynth_library("win32") == folder
    assert os.environ["PATH"].count(str(folder)) == 1


@pytest.mark.parametrize("platform", ["darwin", "linux"])
def test_prepare_does_nothing_elsewhere(platform, monkeypatch):
    monkeypatch.setattr(fsl, "candidate_dirs", lambda: pytest.fail("searched"))
    assert fsl.prepare_fluidsynth_library(platform) is None
    assert os.environ["PATH"] == "C:\\Windows"


@pytest.mark.parametrize(
    "error, platform, expected",
    [
        ("Couldn't find the FluidSynth library.", "win32", "choco install fluidsynth"),
        ("Couldn't find the FluidSynth library.", "win32", "FLUIDSYNTH_DIR"),
        ("Couldn't find the FluidSynth library.", "darwin", "brew install fluid-synth"),
        ("Couldn't find the FluidSynth library.", "linux", "libfluidsynth3"),
        ("No module named 'fluidsynth'", "win32", "pip install pyfluidsynth"),
        ("boom", "linux", "could not be loaded: boom"),
    ],
)
def test_import_error_messages(error, platform, expected):
    assert expected in fsl.import_error_message(error, platform)
