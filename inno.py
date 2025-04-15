import os
from jdxi_editor.project import __version__
inno_exe = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
cwd = os.getcwd()
inno_input_file = r"C:\Users\MBrooks\projects\JDXI-Editor\jdxi_editor.iss"
# inno_input_file = os.path.join(cwd, "jdxi_editor.iss")
inno_cmd = rf'"{inno_exe}" {inno_input_file}'
print(inno_cmd)
os.system(inno_cmd)
