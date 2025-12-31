"""
Draw a VAO with attributes
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_POINTS
from OpenGL.raw.GL.VERSION.GL_1_1 import glDrawArrays

from picogl.buffers.vao.configure import vao_configure_attributes


def vao_draw_with_attributes(attributes: list, atom_count: int, mode: int = GL_POINTS):
    """
    vao_draw_with_attributes

    :param attributes: list Attributes for drawing.
    :param atom_count: int Number of vertices to draw.
    :param mode: int Enum specifying the gl_mode of drawing (default is GL_POINTS).

    Draw the VAO with the specified gl_mode and atom count.
    """
    vao_configure_attributes(attributes)
    glDrawArrays(mode, 0, atom_count)
