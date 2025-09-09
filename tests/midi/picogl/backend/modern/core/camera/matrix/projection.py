import numpy as np
from pyrr import Matrix44


def calculate_projection_matrix(width: int, height: int) -> Matrix44:
    """
    calculate_projection_matrix

    :param width: int
    :param height: int
    :return: Matrix44
    """
    aspect = width / height if height != 0 else 1
    return Matrix44.perspective_projection(
        fovy=45.0, aspect=aspect, near=0.1, far=1000.0
    ).astype(np.float32)
