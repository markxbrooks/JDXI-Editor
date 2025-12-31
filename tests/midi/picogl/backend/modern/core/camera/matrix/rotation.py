"""
3D Rotation Matrix Utilities
============================

This module provides a utility function for generating a combined 3D rotation matrix
using PyGLM, a Python binding for OpenGL Mathematics (GLM). It supports rotation around
the X and Y axes and returns a transformation matrix suitable for use in rendering pipelines.

Dependencies:
-------------
- pyglm (GLM for Python)

Functions:
----------

.. autofunction:: create_rotation_matrix
    Creates a 4x4 rotation matrix from X and Y rotation angles.

Usage Example:
--------------

.. code-block:: python

    rotation_matrix = create_rotation_matrix(angle_x=0.5, angle_y=1.0)
"""

from pyglm import glm


def create_rotation_matrix(angle_x: float, angle_y: float) -> glm.mat4:
    """
    create_rotation_matrix

    :param angle_x: float angle (in radians)
    :param angle_y: float angle (in radians)
    :return: glm.mat4

    Create combined 4x4 3D rotation matrix from x and y angles (in radians),
    using PyGLM's built-in rotation helpers.
    """
    rotation = glm.mat4(1.0)  # identity matrix
    rotation = glm.rotate(rotation, angle_y, glm.vec3(0, 1, 0))  # Y axis
    rotation = glm.rotate(rotation, angle_x, glm.vec3(1, 0, 0))  # X axis
    return rotation
