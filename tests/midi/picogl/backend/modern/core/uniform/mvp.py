import numpy as np
from OpenGL.GL import glUniformMatrix4fv
from OpenGL.raw.GL._types import GL_FALSE
from pyglm import glm

from picogl.backend.modern.core.shader.program import ShaderProgram
from picogl.backend.modern.core.uniform.location import get_uniform_location
from picogl.logger import Logger as log


def set_mvp_uniform(shader: ShaderProgram = None, mvp: glm.mat4 = None) -> None:
    """
    set_mvp_uniform

    :param shader:
    :param mvp:
    :return: None
    Set the model_matrix-view-projection matrix uniform in the shader program.
    """
    mvp_loc = get_uniform_location(shader.program, "mvp_matrix")
    glUniformMatrix4fv(mvp_loc, 1, GL_FALSE, glm.value_ptr(mvp))


def shader_uniform_set_mvp(shader_program: int, mvp_matrix: np.ndarray | glm.mat4):
    """
    shader_uniform_set_mvp

    :param mvp_matrix: np.ndarray or glm.mat4 - model_matrix-view-projection matrix
    :param shader_program: int
    :return: None
    """
    mvp_loc = get_uniform_location(shader_program, "mvp")
    if mvp_loc == -1:
        log.warning("Uniform 'mvp' not found in shader.")
    else:
        # Convert numpy data or glm.mat4 to float pointer
        if isinstance(mvp_matrix, np.ndarray):
            glUniformMatrix4fv(
                mvp_loc, 1, GL_FALSE, mvp_matrix.astype(np.float32).flatten()
            )
        else:
            glUniformMatrix4fv(mvp_loc, 1, GL_FALSE, glm.value_ptr(mvp_matrix))
