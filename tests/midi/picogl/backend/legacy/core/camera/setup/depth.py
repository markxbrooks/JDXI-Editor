"""
Enable depth test
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_DEPTH_TEST, glClearDepth, glEnable


def enable_depth_test() -> None:
    """
    enable_depth_test

    :return: None
    """
    glEnable(GL_DEPTH_TEST)
    glClearDepth(1.0)
