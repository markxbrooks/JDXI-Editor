"""
Generate Normal Data
"""

import numpy as np


def generate_normals(coords: np.ndarray) -> np.ndarray:
    """
    generate_normals

    :param coords: np.ndarray of shape (N, 3)
    :return: np.ndarray of shape (N, 3)
    Simple fake normals pointing up (for testing)
    """
    return np.tile(np.array([0.0, 0.0, 1.0], dtype=np.float32), (len(coords), 1))
