from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_DEPTH_TEST, GL_LESS, glClearColor,
                                          glDepthFunc, glEnable)


def initialize_background() -> None:
    """
    initialize_background

    :return: None
    """
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glClearColor(0.0, 0, 0.4, 0)
