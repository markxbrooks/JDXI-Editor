"""
projection_utils
================

This module provides functions for constructing projection matrices used in
3D graphics, such as perspective projection matrices compatible with OpenGL
and other rendering pipelines.

Functions:
    - perspective: Constructs a 4x4 perspective projection matrix.
"""

import numpy as np


def perspective(fovy: float, aspect: float, znear: float, zfar: float) -> np.ndarray:
    """
    Create a perspective projection matrix.

    :param fovy: Field of view angle in the y-direction, in degrees.
    :type fovy: float
    :param aspect: Aspect ratio of the viewport (width / height).
    :type aspect: float
    :param znear: Distance to the near clipping plane (must be > 0).
    :type znear: float
    :param zfar: Distance to the far clipping plane (must be > znear).
    :type zfar: float

    :return: A 4x4 perspective projection matrix.
    :rtype: numpy.ndarray
    """
    f = 1.0 / np.tan(np.radians(fovy) / 2)
    return np.array(
        [
            [f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [
                0,
                0,
                (zfar + znear) / (znear - zfar),
                (2 * zfar * znear) / (znear - zfar),
            ],
            [0, 0, -1, 0],
        ],
        dtype=np.float32,
    )
