import platform

from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_COLOR_BUFFER_BIT,
                                          GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST,
                                          glClear, glClearColor, glEnable,
                                          glViewport)
from OpenGL.raw.GL.VERSION.GL_3_2 import GL_PROGRAM_POINT_SIZE


def prepare_viewport(width: int, height: int) -> None:
    """
    prepare

    :param width: int
    :param height: int
    :return: None

    Prepares an OpenGL Frame Viewport
    """
    if platform.system() == "Darwin":
        dpr = 2  # macOS Retina displays
    else:
        dpr = 1
    glViewport(0, 0, width * dpr, height * dpr)
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glEnable(GL_PROGRAM_POINT_SIZE)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
