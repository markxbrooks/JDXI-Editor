"""
Enable blending
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_BLEND, GL_ONE_MINUS_SRC_ALPHA,
                                          GL_SRC_ALPHA, glBlendFunc,
                                          glClearColor, glEnable)


def enable_blending() -> None:
    """
    enable_blending

    :return: None
    """
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glClearColor(0.0, 0.0, 0.0, 1.0)
