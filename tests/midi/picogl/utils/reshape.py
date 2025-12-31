""" reshape data to a float 32 row"""
from typing import Any

import numpy as np


def float32_row(array_like: Any) -> np.ndarray:
    """
    Reshape input to a single row and convert to np.float32.

    :param array_like: Any array-like object (list, tuple, np.ndarray).
    :return: A NumPy array of shape (1, N) with dtype np.float32.
    """
    return np.reshape(array_like, (1, -1)).astype(np.float32)
