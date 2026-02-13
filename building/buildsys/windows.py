"""
Windows Builder
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from decologr import Decologr as log, setup_logging

# Disable rich logging on Windows to avoid encoding issues with cp1252
USE_RICH_LOGGING = False

try:
    from jdxi_editor.project import (
        __version__,
        __package_name__,
        __program__,
        __author__,
    )
except ImportError:
    # Fallback if running from different location
    script_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(script_dir.parent.parent))
    from jdxi_editor.project import (
        __version__,
        __package_name__,
        __program__,
        __author__,
    )

# Build configuration
APP_NAME = "JD-Xi Editor.exe"
APP_DISPLAY_NAME = __program__
VERSION = __version__
PKG_IDENTIFIER = "com.jdxi.editor"

def build(ctx):
    project_root = ctx.project_root
    setup_logging(project_name="windows builder", use_rich=USE_RICH_LOGGING)

    clean_build_dirs(project_root)
    build_with_pyinstaller(project_root)
    copy_internal_dirs(project_root)
    run_inno_setup(project_root)

def clean_build_dirs(project_root):
    """Remove previous build artifacts."""
    print("\n🧹 Cleaning previous builds...")

    dirs_to_clean = [
        project_root / "build" / "windows",
        project_root / "build",
        project_root / "dist",
    ]

    files_to_clean = [
        # Add any files to clean here
    ]

    for path in dirs_to_clean:
        if path.exists():
            print(f"  Removing: {path}")
            shutil.rmtree(path)

    for path in files_to_clean:
        if path.exists():
            print(f"  Removing: {path}")
            path.unlink()

    # Also clean pyinstaller artifacts
    pyinstaller_build = project_root / "build"
    if pyinstaller_build.exists():
        for item in pyinstaller_build.iterdir():
            if item.is_dir() and item.name != "windows":
                print(f"  Removing: {item}")
                shutil.rmtree(item)

    print("  ✓ Clean complete")


def remove_build_dirs():
    """remove build dirs"""
    for path in [Path("dist") / __package_name__, Path("build") / __package_name__]:
        if path.exists():
            log.message(f"Removing: {path}")
            shutil.rmtree(path)


def build_with_pyinstaller(project_root):
    """build with pyinstaller"""
    entry_point = project_root / "jdxi_editor" / "main.py"
    entry_point = entry_point.resolve()
    os.chdir(project_root)
    icon_file = project_root / "resources" / "jdxi_icon.ico"
    icon_file = icon_file.resolve()
    try:
        cmd = [
            "pyinstaller.exe",
            "--exclude-module", "PyQt5",
            "-w",
            "-i", str(icon_file),
            "--hidden-import", "numpy",
            "--additional-hooks-dir=.",
            "--paths=env/Lib/site-packages",
            "--noupx",
            "--noconfirm",
            "-n", __package_name__,
            "--clean",
            str(entry_point),
        ]

        dist_files = [icon_file, entry_point]
        for dist_file in dist_files:
            if not dist_file.exists():
                log.message(f"dist_file: {dist_file} not found")
                return
        log.message("Running PyInstaller...")
        subprocess.run(cmd, check=True)
    except Exception as e:
        log.error(f"PyInstaller failed: {e}")
        raise

def copy_internal_dirs(project_root):
    """copy internal directory tree to dist"""
    dest_dir = compose_dest_dir(project_root, package_name=__package_name__)
    os.makedirs(dest_dir, exist_ok=True)
    for folder in [__package_name__, "resources"]:
        src = project_root / folder
        dst = dest_dir / folder
        if src.exists():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)


def compose_dest_dir(project_root, package_name: str):
    """compose dest dir"""
    dist_dir = project_root / "dist"
    dest_dir = dist_dir / package_name / "_internal"
    return dest_dir


def run_inno_setup(project_root):
    """run inno setup"""
    package_name = __package_name__
    iss_file = project_root / f"{package_name}.iss"
    if not iss_file.exists():
        raise FileNotFoundError(f"ISS file not found: {iss_file}")
    inno_exe = Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe")
    if not inno_exe.exists():
        raise FileNotFoundError(f"Inno Setup compiler not found: {inno_exe}")
    cmd = [str(inno_exe), str(iss_file)]
    log.message("Running Inno Setup...")
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    """main entry point"""
    from .context import BuildContext
    
    log.message(f"{__package_name__} version {__version__} build system\n")
    setup_logging(project_name=__package_name__ + " builder", use_rich=USE_RICH_LOGGING)
    try:
        ctx = BuildContext()
        build(ctx)
    except Exception as e:
        log.error(f"Build failed: {e}")
        raise

