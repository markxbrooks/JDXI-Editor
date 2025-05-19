import os
import sys


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    elif getattr(sys, 'frozen', False):  # py2app sets this
        base_path = os.path.join(os.path.dirname(sys.executable), '..', 'Resources')
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
