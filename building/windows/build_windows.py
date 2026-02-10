"""
import os

from jdxi_editor.project import __version__
from distutils.dir_util import copy_tree
from jdxi_editor.project import __package_name__

print(f"{__package_name__} version " + __version__ + " build system")
destination_path_1 = f"dist\\{__package_name__}"
destination_path_2 = rf"build\\{__package_name__}"

rm_cmd = rf'rm -r "{destination_path_1}"'
os.system(rm_cmd)
rm_cmd = rf'rm -r "{destination_path_2}"'
os.system(rm_cmd)
## With console = pyinstaller_cmd + --console
pyinstaller_cmd = rf"pyinstaller.exe --exclude-module PyQt5 -w -i  designer\icons\{__package_name__}.ico --hidden-import numpy --additional-hooks-dir=. --paths=env\Lib\site-packages --noupx --noconfirm -n {__package_name__} --clean main.py"

os.system(pyinstaller_cmd)                                                                                                                                                                                                                  

dest_dir = f"dist/{__package_name__}/_internal"
dir_list = [__package_name__, "resources"]
for directory in dir_list:
    copy_tree(directory, dest_dir + r"/" + directory)
inno_input_file = os.path.join(os.getcwd(), f"{__package_name__}.iss")                                                                                                                                                                                                      
## With console
# pyinstaller_cmd = r"pyinstaller.exe -w -i  resources\jdxi_icon.ico --console --additional-hooks-dir=. --paths=env\Lib\site-packages --noupx --noconfirm -n jdxi_editor --clean main.py"
## Without console
pyinstaller_cmd = rf"pyinstaller.exe -w -i resources\jdxi_icon.ico --exclude-module PyQt5 --additional-hooks-dir=. --paths=env\Lib\site-packages --noupx --noconfirm -n {__package_name__} --clean {__package_name__}\main.py"
os.system(pyinstaller_cmd)
dir_list = [__package_name__]
dest_dir = f"dist/{__package_name__}"
for directory in dir_list:
    for directory in dir_list:
        copy_tree(directory, dest_dir + r"/" + directory)
inno_exe = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
cwd = os.getcwd()
inno_cmd = rf'"{inno_exe}" {inno_input_file}'
print(inno_cmd)
os.system(inno_cmd)

"""

import os, sys
import subprocess
import shutil
from pathlib import Path
from decologr import Decologr as log, setup_logging

# from jdxi_editor.project import __version__, __package_name__

# Import project metadata
# Navigate up from building/apple/ to project root
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from jdxi_editor.project import (
        __version__,
        __package_name__,
        __program__,
        __author__,
    )
except ImportError:
    # Fallback if running from different location
    sys.path.insert(0, str(SCRIPT_DIR.parent.parent))
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
INSTALL_LOCATION = "/Applications"

# Directories
BUILD_DIR = PROJECT_ROOT / "build" / "macos"
DIST_DIR = PROJECT_ROOT / "dist"
VENV_PATH = PROJECT_ROOT / "venv"
PYTHON_PATH = VENV_PATH / "bin" / "python"


def clean_build_dirs():
    """Remove previous build artifacts."""
    print("\n🧹 Cleaning previous builds...")

    dirs_to_clean = [
        BUILD_DIR,
        PROJECT_ROOT / "build",
        PROJECT_ROOT / "dist",
    ]

    files_to_clean = [
        # PROJECT_ROOT / f"JD-Xi_Editor_{VERSION}_MacOS_Universal.pkg",
        # PROJECT_ROOT / f"JD-Xi_Editor_{VERSION}_MacOS_Universal.dmg",
    ]

    for path in dirs_to_clean:
        if path.exists():
            print(f"  Removing: {path}")
            shutil.rmtree(path)

    for path in files_to_clean:
        if path.exists():
            print(f"  Removing: {path}")
            path.unlink()

    # Also clean py2app artifacts
    py2app_build = PROJECT_ROOT / "build"
    py2app_dist = PROJECT_ROOT / "dist" / APP_NAME
    if py2app_build.exists():
        for item in py2app_build.iterdir():
            if item.is_dir() and item.name != "macos":
                print(f"  Removing: {item}")
                shutil.rmtree(item)

    print("  ✓ Clean complete")


def remove_build_dirs():
    """remove build dirs"""
    for path in [Path("dist") / __package_name__, Path("build") / __package_name__]:
        if path.exists():
            log.message(f"Removing: {path}")
            shutil.rmtree(path)


def build_with_pyinstaller():
    """build with pyinstaller"""
    entry_point = Path(PROJECT_ROOT) / "jdxi_editor" / "main.py"
    entry_point = entry_point.resolve()
    os.chdir(PROJECT_ROOT)
    icon_file = Path(PROJECT_ROOT) / "resources" / "jdxi_icon.ico"
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

def copy_internal_dirs():
    """copy internal directory tree to dist"""
    dest_dir = compose_dest_dir(package_name=__package_name__)
    os.makedirs(dest_dir, exist_ok=True)
    for folder in [__package_name__, "resources"]:
        shutil.copytree(folder, str(dest_dir / folder))


def compose_dest_dir(package_name: str):
    """compose dest dir"""
    dist_dir = Path("dist")
    dest_dir = dist_dir / package_name / "_internal"
    return dest_dir


def run_inno_setup():
    """run inno setup"""
    package_name = __package_name__  # assuming this exists in your module
    iss_file = Path.cwd() / f"{package_name}.iss"
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
    log.message(f"{__package_name__} version {__version__} build system\n")
    setup_logging(project_name=__package_name__+ " builder", use_rich=True)
    try:
        clean_build_dirs()
        build_with_pyinstaller()
        copy_internal_dirs()
        run_inno_setup()
    except Exception as e:
        log.error(f"Build failed: {e}")
        raise

