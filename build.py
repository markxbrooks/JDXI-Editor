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

import os
import shutil
import subprocess
from distutils.dir_util import copy_tree
from jdxi_editor.project import __version__, __package_name__

def remove_build_dirs():
    for path in [f"dist/{__package_name__}", f"build/{__package_name__}"]:
        if os.path.exists(path):
            print(f"Removing: {path}")
            shutil.rmtree(path)

def build_with_pyinstaller():
    cmd = [
        "pyinstaller.exe",
        "--exclude-module", "PyQt5",
        "-w",
        "-i", os.path.join("designer", "icons", f"{__package_name__}.ico"),
        "--hidden-import", "numpy",
        "--additional-hooks-dir=.",
        "--paths=env/Lib/site-packages",
        "--noupx",
        "--noconfirm",
        "-n", __package_name__,
        "--clean",
        os.path.join(__package_name__, "main.py"),
    ]
    print("Running PyInstaller...")
    subprocess.run(cmd, check=True)

def copy_internal_dirs():
    dest_dir = os.path.join("dist", __package_name__, "_internal")
    os.makedirs(dest_dir, exist_ok=True)
    for folder in [__package_name__, "resources"]:
        copy_tree(folder, os.path.join(dest_dir, folder))

def run_inno_setup():
    iss_file = os.path.join(os.getcwd(), f"{__package_name__}.iss")
    inno_exe = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    cmd = [inno_exe, iss_file]
    print("Running Inno Setup...")
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    print(f"{__package_name__} version {__version__} build system\n")
    remove_build_dirs()
    build_with_pyinstaller()
    copy_internal_dirs()
    run_inno_setup()

