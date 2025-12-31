"""
OpenGL Camera Matrix Update Utility
===================================

This module provides a function to update the OpenGL modelview matrix based on
camera parameters such as translation (panning), rotation (orbit angles), and zoom.
It is typically used in interactive 3D applications to reflect user-controlled
camera movements in the rendering pipeline.

Dependencies:
-------------
- numpy
- PyOpenGL

Functions:
----------

.. autofunction:: update_camera_matrix
    Updates the OpenGL modelview matrix using translation, rotation, and zoom values.

Parameters:
-----------
- `translation`: NumPy array of shape `(2,)` representing X and Y panning.
- `rotation`: NumPy array of shape `(3,)` representing rotation angles in degrees around X, Y, and Z axes.
- `zoom_value`: Float representing zoom along the Z-axis.

Usage Example:
--------------

.. code-block:: python

    update_camera_matrix(
        translation=np.array([0.1, -0.2]),
        rotation=np.array([30.0, 45.0, 0.0]),
        zoom_value=-5.0
    )
"""

import numpy as np
from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_MODELVIEW, glLoadIdentity,
                                          glMatrixMode, glRotatef,
                                          glTranslatef)


def update_camera_matrix(
    translation: np.ndarray, rotation: np.ndarray, zoom_value: float
) -> None:
    """
    update_camera_matrix

    :param translation: np.ndarray of shape (2,) - [x_pan, y_pan]
    :param rotation: np.ndarray of shape (3,) - [x_rot, y_rot, z_rot] in degrees
    :param zoom_value: float - zoom along z-axis

    Updates the OpenGL modelview matrix using translation, rotation, and zoom values.
    """
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Apply zoom and pan
    glTranslatef(
        float(translation[0]),
        float(translation[1]),
        float(zoom_value),
    )

    # Apply rotations in Z-Y-X order (typical camera orbit)
    glRotatef(float(rotation[2]), 0.0, 0.0, 1.0)  # Z
    glRotatef(float(rotation[1]), 0.0, 1.0, 0.0)  # Y
    glRotatef(float(rotation[0]), 1.0, 0.0, 0.0)  # X
