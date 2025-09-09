import numpy as np

MVP_ZOOM_SCALE = -0.0015


def compute_mvp_zoom_from_zoom(zoom_value: float) -> float:
    """
    compute_mvp_zoom_from_zoom
    :param zoom_value: float
    :return: float
    Compute the MVP zoom factor from a zoom value.
    """

    return MVP_ZOOM_SCALE * zoom_value


def compute_zoom_from_mvp_zoom(mvp_zoom: float) -> float:
    """
    compute_zoom_from_mvp_zoom

    :param mvp_zoom: float
    :return: float
    """
    return mvp_zoom / MVP_ZOOM_SCALE


def invert_mvp_matrix(
    projection: np.ndarray, model_view: np.ndarray
) -> np.ndarray | None:
    """
    invert_mvp_matrix
    :param projection: 4x4 projection matrix
    :param model_view: np.ndarray
    :return: np.ndarray
    Compute inverse of MVP matrix
    """
    mvp_matrix = np.dot(projection, model_view)
    try:
        inverse_mvp_matrix = np.linalg.inv(mvp_matrix)
        return inverse_mvp_matrix
    except np.linalg.LinAlgError:
        return None


def create_normalized_device_vector(
    ndc_x: float, ndc_y: float, ndc_z: float
) -> np.ndarray:
    """
    create_normalized_device_vector

    :param ndc_x: float normalized device x coordinate 0.0-1.0
    :param ndc_y: float normalized device y coordinate 0.0-1.0
    :param ndc_z: float normalized device z coordinate 0.0-1.0
    :return: np.ndarray normalized_device_vector

    Create normalized device coordinate vector
    """

    normalized_device_vector = np.array([ndc_x, ndc_y, ndc_z, 1.0], dtype=np.float32)
    return normalized_device_vector


def normalize_device_coordinates(depth, viewport, x, y):
    """
    normalize_device_coordinates

    :param depth: float
    :param viewport: np.ndarray
    :param x: int
    :param y: int
    :return: float, float, float
    """
    # Normalize device coordinates
    ndc_x = (x - viewport[0]) / viewport[2] * 2.0 - 1.0
    ndc_y = (y - viewport[1]) / viewport[3] * 2.0 - 1.0
    ndc_y = -ndc_y  # Flip Y axis (OpenGL vertex_shader screen coordinates)
    ndc_z = depth * 2.0 - 1.0
    return ndc_x, ndc_y, ndc_z


def convert_to_world_coordinates(inverse_mvp_matrix, normalized_device_vector):
    """
    convert_to_world_coordinates
    :param inverse_mvp_matrix: np.ndarray inverse_mvp_matrix
    :param normalized_device_vector: np.ndarray normalized_device_vector
    :return: np.ndarray world_coordinates
    """
    world_coords = inverse_mvp_matrix @ normalized_device_vector
    return world_coords
