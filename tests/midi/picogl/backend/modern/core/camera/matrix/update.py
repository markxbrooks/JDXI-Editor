import numpy as np


def update_camera_matrix(
    view_translation: np.ndarray,
    view_rotation: np.ndarray,
    view_zoom_parameter_value: float,
) -> np.ndarray:
    """

    update_camera_matrix_numpy

    :param view_translation: np.ndarray
    :param view_rotation: np.ndarray
    :param view_zoom_parameter_value: float
    :return: np.ndarray

    Returns a 4x4 model_matrix matrix combining zoom, pan, and rotation.
    """
    # Translation (pan + zoom)
    translate = np.identity(4, dtype=np.float32)
    translate[3, 0:3] = [
        view_translation[0],
        view_translation[1],
        view_zoom_parameter_value,
    ]

    # Rotation X
    rx = np.identity(4, dtype=np.float32)
    theta = np.radians(view_rotation[0])
    rx[1, 1] = np.cos(theta)
    rx[1, 2] = -np.sin(theta)
    rx[2, 1] = np.sin(theta)
    rx[2, 2] = np.cos(theta)

    # Rotation Y
    ry = np.identity(4, dtype=np.float32)
    theta = np.radians(view_rotation[1])
    ry[0, 0] = np.cos(theta)
    ry[0, 2] = np.sin(theta)
    ry[2, 0] = -np.sin(theta)
    ry[2, 2] = np.cos(theta)

    # Rotation Z
    rz = np.identity(4, dtype=np.float32)
    theta = np.radians(view_rotation[2])
    rz[0, 0] = np.cos(theta)
    rz[0, 1] = -np.sin(theta)
    rz[1, 0] = np.sin(theta)
    rz[1, 1] = np.cos(theta)

    # Final model_matrix matrix: Translate * Rz * Ry * Rx
    model = translate @ rz @ ry @ rx
    return model
