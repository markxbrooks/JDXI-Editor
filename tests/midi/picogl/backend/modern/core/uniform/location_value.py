from typing import Union

import numpy as np
from OpenGL.GL import * # pylint: disable=W0614
from OpenGL.GL import glUniformMatrix4fv
from pyglm import glm

from picogl.logger import Logger as log


def set_uniform_location_value(
    location: int,
    uniform_value: Union[
        float, int, glm.vec2, glm.vec3, glm.vec4, glm.mat4, np.ndarray
    ],
):
    """
    set_uniform_value

    :param uniform location:  int
    :param uniform_value: Value to set (supports float, int, vec2, vec3, vec4, mat4, or np.ndarray)

    Set a uniform variable in a shader program
    """
    # Handle types
    if isinstance(uniform_value, float):
        glUniform1f(location, uniform_value)
    elif isinstance(uniform_value, int):
        glUniform1i(location, uniform_value)
    elif isinstance(uniform_value, glm.vec2):
        glUniform2fv(location, 1, glm.value_ptr(uniform_value))
    elif isinstance(uniform_value, glm.vec3):
        glUniform3fv(location, 1, glm.value_ptr(uniform_value))
    elif isinstance(uniform_value, glm.vec4):
        glUniform4fv(location, 1, glm.value_ptr(uniform_value))
    elif isinstance(uniform_value, glm.mat4):
        glUniformMatrix4fv(location, 1, GL_FALSE, glm.value_ptr(uniform_value))
    elif isinstance(uniform_value, np.ndarray):
        if uniform_value.shape == (4, 4):  # mat4
            glUniformMatrix4fv(
                location, 1, GL_FALSE, uniform_value.astype(np.float32).flatten()
            )
        elif uniform_value.shape == (3,):  # vec3
            glUniform3fv(location, 1, uniform_value.astype(np.float32))
        elif uniform_value.shape == (4,):  # vec4
            glUniform4fv(location, 1, uniform_value.astype(np.float32))
        else:
            log.warning(
                f"Unsupported ndarray shape {uniform_value.shape} for uniform '{location}'"
            )
    else:
        log.warning(f"Unsupported uniform type for '{location}': {type(uniform_value)}")
