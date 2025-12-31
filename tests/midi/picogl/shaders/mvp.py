import numpy as np
from OpenGL.GL import glUniformMatrix4fv
from OpenGL.raw.GL._types import GL_FALSE
from pyglm import glm

from picogl.backend.modern.core.shader.helpers import log_gl_error


def calculate_mvp_matrix(context: object,
                         width: int = 1920,
                         height: int = 1080):
    """
    calculate_mvp_matrix

    :param context: GlContext
    :param width: int
    :param height: int
    """
    context.projection = glm.perspective(
        glm.radians(45.0), float(width) / float(height), 0.1, 1000.0
    )
    context.view = glm.lookAt(
        glm.vec3(4, 3, -3),  # Camera is at (4,3,-3), in World Space
        glm.vec3(0, 0, 0),  # and looks at the (0.0.0))
        glm.vec3(0, 1, 0),
    )  # Head is up (set to 0,-1,0 to look upside-down)
    context.model = glm.mat4(1.0)
    context.mvp_matrix = context.projection * context.view * context.model


def set_mvp_matrix_to_uniform_id(mvp_id: int, mvp_matrix: np.ndarray) -> None:
    """
    set_mvp_matrix_to_uniform_id

    :param mvp_id: int
    :param mvp_matrix: np.ndarray
    :return: None
    """
    glUniformMatrix4fv(mvp_id, 1, GL_FALSE, glm.value_ptr(mvp_matrix))
    log_gl_error()
