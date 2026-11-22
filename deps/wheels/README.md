# Prebuilt wheels for building the installers

A local wheelhouse for dependencies that have no wheel on PyPI for the machine
doing the build, so `pip` does not have to compile them. It is for **building
this project's installers**, not for the published package: nothing in here is
shipped to PyPI, and `pip install JDXI-Editor` never sees it.

Prime a build environment with:

```bash
pip install --find-links deps/wheels -e .
```

## Nothing in here is required now

USB recording and SoundFont output use `sounddevice`. Its wheels include
PortAudio for macOS, Linux, and Windows, so a checkout does not compile
PortAudio and does not need a PyAudio wheel. `.gitignore` still ignores any
wheels dropped in this folder.

`fluidsynth/bin` is different: those libraries are committed, loaded by name
at runtime, and one copy serves every Python.
