# run_editor.py
"""Entry point for JD-Xi Editor. Bootstrap env before any imports."""
import os
import sys

# py2app bundles don't inherit shell env; set HOMEBREW_PREFIX so pyfluidsynth
# can find libfluidsynth when launched from Finder (fluid-synth from Homebrew)
if not os.environ.get("HOMEBREW_PREFIX") and sys.platform == "darwin":
    for prefix in ("/opt/homebrew", "/usr/local"):
        lib_path = os.path.join(prefix, "lib", "libfluidsynth.dylib")
        if os.path.exists(lib_path):
            os.environ["HOMEBREW_PREFIX"] = prefix
            break

if __name__ == "__main__":
    from jdxi_editor.main import main

    main()
