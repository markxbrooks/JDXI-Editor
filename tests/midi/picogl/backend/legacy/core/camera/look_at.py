"""
look_at.py

This module provides a utility function for constructing a view matrix,
commonly used in 3D graphics to simulate a camera's perspective.

The `look_at` function generates a 4×4 transformation matrix that positions
and orients a virtual camera in world space. It takes the camera's position,
a target point to look at, and an up direction vector to define the camera's
orientation.

Typical use cases include:
- Setting up camera views in OpenGL or other rendering engines
- Transforming world coordinates into view (camera) space
- Creating custom camera systems for simulations or games

Function:
    look_at(eye, target, up) -> np.ndarray
        Constructs a view matrix from camera position, target, and up vector.
"""

import numpy as np


def look_at(eye: np.ndarray, target: np.ndarray, up: np.ndarray) -> np.ndarray:
    """
    look_at

    :param eye: np.array 3D position of the camera (shape: (3,))
    :param target: np.array 3D position the camera is looking at (shape: (3,))
    :param up: np.array Up direction vector (shape: (3,))
    :return: np.array 4x4 v

    Constructs a view matrix simulating a camera looking from 'eye' to 'target'.
    """
    f = target - eye
    f = f / np.linalg.norm(f)
    s = np.cross(f, up)
    s = s / np.linalg.norm(s)
    u = np.cross(s, f)

    m = np.identity(4, dtype=np.float32)
    m[0, :3] = s
    m[1, :3] = u
    m[2, :3] = -f
    m[:3, 3] = -eye @ np.stack([s, u, -f], axis=1)
    return m
