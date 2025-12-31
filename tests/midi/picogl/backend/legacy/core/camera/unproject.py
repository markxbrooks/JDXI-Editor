"""
Unproject
"""

from typing import Optional, Tuple

import numpy as np
from OpenGL.GL import glGetDoublev, glGetIntegerv
from OpenGL.GLU import gluUnProject
from OpenGL.raw.GL._types import GL_FLOAT
from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_DEPTH_COMPONENT, GL_DEPTH_TEST,
                                          GL_MODELVIEW_MATRIX,
                                          GL_PROJECTION_MATRIX, GL_VIEWPORT,
                                          glFlush, glIsEnabled, glReadPixels)

from picogl.logger import Logger as log


def unproject(x: int, y: int) -> Optional[Tuple[float, float, float]]:
    """
    unproject

    :param x: x coordinate
    :param y: y coordinate
    :return: Tuple[int, int, int] coordinate_data_main

    Un-projects screen coordinate_data_main (x, y) into 3D world coordinate_data_main.
    Assumes OpenGL context is current -Ensure OpenGL context is current if needed
    i.e. self.makeCurrent() ← must be called before this if in Qt widget
    """
    model_view = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)
    viewport = glGetIntegerv(GL_VIEWPORT)

    y_gl = viewport[3] - y

    if not (0 <= x < viewport[2] and 0 <= y_gl < viewport[3]):
        log.message(f"Coordinates out of bounds: ({x}, {y_gl})")
        return None

    if not glIsEnabled(GL_DEPTH_TEST):
        log.warning("Warning: GL_DEPTH_TEST is not enabled")

    # Read depth safely
    depth = np.array([0.0], dtype=np.float32)
    try:
        glFlush()
        glReadPixels(x, y_gl, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT, depth)
    except Exception as ex:
        log.error(f"glReadPixels failed: {ex}")
        return None

    wz = float(depth[0])
    if wz == 1.0:
        return None

    wx, wy, wz = gluUnProject(x, y_gl, wz, model_view, projection, viewport)
    return wx, wy, wz
