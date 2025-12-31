from OpenGL.GL import glDrawElements
from OpenGL.raw.GL._types import GL_UNSIGNED_INT
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_LINES
from OpenGL.raw.GL.VERSION.GL_3_0 import glBindVertexArray


def draw_elements(
    vao: int, index_count: int, mode: int = GL_LINES, index_type: int = GL_UNSIGNED_INT
):
    """
    Helper method to bind a VAO and draw its elements.

    :param vao: Vertex Array Object to bind
    :param index_count: Number of indices to draw
    :param mode: Drawing gl_mode (e.g., GL_LINES, GL_TRIANGLES)
    :param index_type: Type of indices (e.g., GL_UNSIGNED_INT)
    """
    glBindVertexArray(vao)
    glDrawElements(mode, index_count, index_type, None)
    glBindVertexArray(0)
