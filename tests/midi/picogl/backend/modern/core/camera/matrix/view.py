import numpy as np
from pyrr import Matrix44, Vector3


def calculate_view_matrix(cam_pos, cam_target):
    return Matrix44.look_at(
        eye=Vector3(cam_pos), target=Vector3(cam_target), up=Vector3([0.0, 1.0, 0.0])
    ).astype(np.float32)
