"""Linux packages: a pre-release sorts before its release (dpkg and rpm put «1.0.0rc1» after 1.0.0)."""

import shutil
import subprocess

import pytest

from jdxi_editor.project import package_version


@pytest.mark.parametrize("pep440, package", [
    ("1.0.0", "1.0.0"),
    ("1.0.0rc1", "1.0.0~rc1"),
    ("1.0.0b2", "1.0.0~b2"),
    ("1.0.0a1", "1.0.0~a1"),
    ("1.0.1.dev3", "1.0.1~dev3"),
    ("1.0.0rc1.dev2", "1.0.0~rc1~dev2"),
    ("1.0.0.post1", "1.0.0+post1"),
])
def test_package_version(pep440, package):
    assert package_version(pep440) == package


@pytest.mark.skipif(shutil.which("dpkg") is None, reason="dpkg not installed")
def test_dpkg_orders_them_as_releases():
    order = ["1.0.0b2", "1.0.0rc1", "1.0.0rc2", "1.0.0", "1.0.0.post1", "1.0.1"]
    versions = [package_version(v) for v in order]
    for older, newer in zip(versions, versions[1:]):
        assert subprocess.run(["dpkg", "--compare-versions", older, "lt", newer]).returncode == 0, (older, newer)
