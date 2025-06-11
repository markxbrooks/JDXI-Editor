import os
import platform
import subprocess

from jdxi_editor.log.logger import Logger as log
from jdxi_editor.resources import resource_path


def documentation_file_path(file_name: str) -> str:
    """
    documentation_file_path

    :param file_name: str The file name to return a path for the documentation file
    :return: str The file path
    """
    return resource_path(os.path.join("doc", "build", "html", file_name))


def os_file_open(file_name: str) -> None:
    """
    os_file_open

    :param file_name:  str
    :return None:
    Opens a file using default program from the OS
    """
    if not os.path.exists(file_name):
        return
    try:
        if platform.system() == 'Darwin':  # macOS
            subprocess.call(['open', file_name])
        elif platform.system() == 'Windows':  # Windows
            os.startfile(file_name)
        else:  # linux variants
            subprocess.call(['xdg-open', file_name])
    except OSError as error:
        log.error(f"Error opening file: {error}")
