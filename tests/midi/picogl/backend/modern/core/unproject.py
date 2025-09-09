"""
Modern OpenGL Unproject Function
"""

from typing import Any, Tuple

import numpy as np

from picogl.backend.modern.core.mvp import (convert_to_world_coordinates,
                                            create_normalized_device_vector,
                                            invert_mvp_matrix,
                                            normalize_device_coordinates)


def unproject(
    x: int,
    y: int,
    depth: float,
    model_view: np.ndarray,
    projection: np.ndarray,
    viewport: Tuple[int, int, int, int],
) -> tuple[Any, ...] | None:
    """
    unproject

    :param x: X screen coordinate
    :param y: Y screen coordinate
    :param depth: Depth value from depth buffer (range 0.0 - 1.0)
    :param model_view: 4x4 model_matrix-view matrix
    :param projection: 4x4 projection matrix
    :param viewport: Viewport tuple (x, y, width, height)
    :return: (x, y, z) in world space, or None if invalid

    Unprojects 2D screen coordinates into 3D world coordinates in modern OpenGL.
    """
    if depth == 1.0:
        return None  # Depth of 1.0 means background

    ndc_x, ndc_y, ndc_z = normalize_device_coordinates(depth, viewport, x, y)

    normalized_device_vector = create_normalized_device_vector(ndc_x, ndc_y, ndc_z)

    inverse_mvp_matrix = invert_mvp_matrix(projection, model_view)

    world_coords = convert_to_world_coordinates(
        inverse_mvp_matrix, normalized_device_vector
    )
    if world_coords[3] == 0.0:
        return None

    # Perspective divide
    world_coords /= world_coords[3]
    return tuple(world_coords[:3])
