import os

from jdxi_editor.project import __version__
from distutils.dir_util import copy_tree
print("jdxi_editor version " + __version__ + " build system")
destination_path_1 = f"dist\\jdxi_editor"
destination_path_2 = rf"build\\jdxi_editor"

rm_cmd = rf'rm -r "{destination_path_1}"'
os.system(rm_cmd)
rm_cmd = rf'rm -r "{destination_path_2}"'
os.system(rm_cmd)
## With console = pyinstaller_cmd + --console
pyinstaller_cmd = r"pyinstaller.exe --exclude-module PyQt5 -w -i  designer\icons\jdxi_editor.ico --hidden-import numpy --additional-hooks-dir=. --paths=env\Lib\site-packages --noupx --noconfirm -n jdxi_editor --clean main.py"

os.system(pyinstaller_cmd)

dest_dir = "dist/jdxi_editor/_internal"
dir_list = ["jdxi_editor", "resources"]
for directory in dir_list:
    copy_tree(directory, dest_dir + r"/" + directory)
inno_input_file = r"C:\Users\MBrooks\projects\JDXI-Editor\jdxi_editor.iss"
## With console
# pyinstaller_cmd = r"pyinstaller.exe -w -i  resources\jdxi_icon.ico --console --additional-hooks-dir=. --paths=env\Lib\site-packages --noupx --noconfirm -n jdxi_editor --clean main.py"
## Without console
pyinstaller_cmd = r"pyinstaller.exe -w -i resources\jdxi_icon.ico --exclude-module PyQt5 --additional-hooks-dir=. --paths=env\Lib\site-packages --noupx --noconfirm -n jdxi_editor --clean jdxi_editor\main.py"
os.system(pyinstaller_cmd)
dir_list = ["jdxi_editor"]
dest_dir = "dist/jdxi_editor"
for directory in dir_list:
    for directory in dir_list:
        copy_tree(directory, dest_dir + r"/" + directory)
inno_exe = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
cwd = os.getcwd()
# inno_input_file = os.path.join(cwd, "jdxi_editor.iss")
inno_cmd = rf'"{inno_exe}" {inno_input_file}'
print(inno_cmd)
os.system(inno_cmd)
