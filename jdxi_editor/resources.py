import os
import sys


def resource_path(relative_path: str) -> str:
    """
    resource_path
    :param relative_path: str
    :return:
    """
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
