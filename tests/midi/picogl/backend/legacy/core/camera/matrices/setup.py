"""
OpenGL Matrix Retrieval Utility
===============================

This module provides a helper function to retrieve transformation matrices
from the OpenGL state machine. It uses `glGetFloatv` to query matrices such as
the modelview or projection matrix and returns them in a format compatible with GLSL.

Dependencies:
-------------
- numpy
- PyOpenGL

Functions:
----------

.. autofunction:: get_matrix
    Retrieves a 4x4 matrix from OpenGL and transposes it to match GLSL's column-major format.

Parameters:
-----------
- `mode`: OpenGL matrix mode (e.g., GL_MODELVIEW_MATRIX, GL_PROJECTION_MATRIX).

Returns:
--------
- A NumPy array of shape `(4, 4)` representing the requested matrix.

Usage Example:
--------------

.. code-block:: python

    modelview_matrix = get_matrix(GL_MODELVIEW_MATRIX)
    projection_matrix = get_matrix(GL_PROJECTION_MATRIX)
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_PROJECTION, glLoadIdentity,
                                          glMatrixMode)
from OpenGL.raw.GLU import gluPerspective


def setup_matrices(aspect: float):
    """
    setup_matrices

    :param aspect: float Aspect ratio
    :return: None
    """
    # Set up projection matrix
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, aspect, 0.1, 1000.0)
    # Set up model_matrix view matrix with camera and user transforms
