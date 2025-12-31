from functools import wraps

from OpenGL.GL import glGetIntegerv
from OpenGL.raw.GL.VERSION.GL_2_0 import GL_CURRENT_PROGRAM, glUseProgram
from OpenGL.raw.GL.VERSION.GL_3_0 import (GL_VERTEX_ARRAY_BINDING,
                                          glBindVertexArray)


def preserve_gl_state(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        prev_vao = glGetIntegerv(GL_VERTEX_ARRAY_BINDING)
        prev_program = glGetIntegerv(GL_CURRENT_PROGRAM)
        try:
            return func(*args, **kwargs)
        finally:
            glBindVertexArray(prev_vao)
            glUseProgram(prev_program)

    return wrapper
