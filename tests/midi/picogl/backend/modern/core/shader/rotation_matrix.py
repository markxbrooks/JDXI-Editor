"""
Module for creating rotation matrices.
"""

import numpy as np


def create_rotation_matrix(angle_x: float, angle_y: float) -> np.ndarray:
    """
    create_rotation_matrix

    :param angle_x: float
    :param angle_y: float
    :return: np.ndarray
    """

    Rx = np.array(
        [
            [1, 0, 0, 0],
            [0, np.cos(angle_x), -np.sin(angle_x), 0],
            [0, np.sin(angle_x), np.cos(angle_x), 0],
            [0, 0, 0, 1],
        ],
        dtype=np.float32,
    )

    Ry = np.array(
        [
            [np.cos(angle_y), 0, np.sin(angle_y), 0],
            [0, 1, 0, 0],
            [-np.sin(angle_y), 0, np.cos(angle_y), 0],
            [0, 0, 0, 1],
        ],
        dtype=np.float32,
    )

    return Ry @ Rx
