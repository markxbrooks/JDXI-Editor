from pathlib import Path
import sys

class BuildContext:
    def __init__(self):
        self.project_root = self._find_project_root()
        self.venv_python = self._find_venv_python()

    def _find_project_root(self) -> Path:
        here = Path(__file__).resolve()
        for parent in here.parents:
            if (parent / "pyproject.toml").exists():
                return parent
            if (parent / "jdxi_editor").exists():
                return parent
        raise RuntimeError("Could not locate project root")

    def _find_venv_python(self) -> Path:
        """
        The interpreter of the project's own virtualenv.

        Both names are accepted, ``.venv`` first: the checkout in this
        repository uses that one, the release workflow creates it on macOS and
        Linux, and a build that insists on the other name fails before it has
        begun with nothing to say but "Virtualenv missing". The paths tried are
        named in the error so the next such failure explains itself.
        """
        if sys.platform == "win32":
            relative = Path("Scripts") / "python.exe"
        else:
            relative = Path("bin") / "python"

        tried = [self.project_root / name / relative for name in (".venv", "venv")]
        for python in tried:
            if python.exists():
                return python

        raise RuntimeError(
            "Virtualenv missing: looked for "
            + " and ".join(str(path) for path in tried)
        )
