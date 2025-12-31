from OpenGL.raw.GL.VERSION.GL_1_0 import GL_NO_ERROR, glGetError
from OpenGL.raw.GLU import gluErrorString

from picogl.logger import Logger as log


def check_errors():
    """
    check_errors

    :return:
    """
    error = glGetError()
    if error != GL_NO_ERROR:
        log.message(f"GL ERROR: {gluErrorString(error)}")


def check_error_after(label: str = "") -> None:
    """
    check_error_after

    :param label: str
    :return: None
    """
    err = glGetError()
    if err != GL_NO_ERROR:
        log.error(f"⚠️ OpenGL error after {label}: {err}")
