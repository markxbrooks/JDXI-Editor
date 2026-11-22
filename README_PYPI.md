## PYPI Release Mechanism

```commandline
  cd ~/projects/JDXI-Editor
  rm -rf dist
  .venv/bin/python -m build
  .venv/bin/python -m twine check --strict dist/*
  # Using uv
  # uvx twine check --strict dist/*
  # uvx --from build pyproject-build
  .venv/bin/python -m twine upload dist/*
  username: __token__
```