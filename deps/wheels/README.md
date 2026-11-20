# Prebuilt wheels for building the installers

A local wheelhouse for dependencies that have no wheel on PyPI for the machine
doing the build, so `pip` does not have to compile them. It is for **building
this project's installers**, not for the published package: nothing in here is
shipped to PyPI, and `pip install JDXI-Editor` never sees it.

Prime a build environment with:

```bash
pip install --find-links deps/wheels -e .
```

## What needs to be in here, and why

**PyAudio** (`jdxi_editor/midi/recording/`, `jdxi_editor/ui/widgets/usb/`) has no
macOS arm64 wheel on PyPI at all — `pip download pyaudio --only-binary :all:`
returns nothing — so every Apple Silicon machine compiles it from source.

On macOS 26/27 that compile links against the newest SDK and fails:

```
ld: tapi error: malformed file
.../SDKs/MacOSX27.2.sdk/usr/lib/libSystem.B.tbd:4:20: error: unknown architecture
```

Homebrew's Python 3.10 records `MACOSX_DEPLOYMENT_TARGET = 15` and no
`isysroot`, so it picks the newest SDK installed, which the toolchain then
cannot link. Pin an older SDK and it builds:

```bash
SDKROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX26.sdk \
  pip wheel pyaudio --no-deps -w deps/wheels
```

`ls /Library/Developer/CommandLineTools/SDKs/` shows which SDKs you have.

## The wheels are not committed

`.gitignore` keeps this README and ignores the wheels themselves. They are
per-interpreter and per-architecture — `pyaudio-0.2.14-cp310-cp310-macosx_15_0_arm64.whl`
is good for CPython 3.10 on arm64 and nothing else — so a committed one would
be useless on most machines and stale on the rest. Rebuild them with the
command above on whichever machine builds the installers.

Unlike `fluidsynth/bin`, which *is* committed: those are plain native
libraries loaded by name at runtime, so one copy serves every Python. A
CPython extension module cannot be shared that way.

## This is a build-side workaround, not the fix

The frozen builds already bundle PyAudio (py2app and PyInstaller follow the
module-level `import pyaudio`), so installer users are fine. Users who
`pip install` on macOS arm64 are not: they hit the compile above. The real fix
is to record through `sounddevice`, which is already a dependency, ships
PortAudio binaries for every platform, needs no compiler, and is already used
for input in `jdxi_editor/audio/audio_source.py`. PyAudio would then go away.
