import numpy as np
from OpenGL.raw.GL.VERSION.GL_1_0 import glGetFloatv


def get_matrix(mode: int) -> np.ndarray:
    """
    get_matrix

    :param mode: int
    :return: np.ndarray
    """
    mat = np.zeros((4, 4), dtype=np.float32)
    glGetFloatv(mode, mat)
    return mat.T  # Transpose to match GLSL column-major order
