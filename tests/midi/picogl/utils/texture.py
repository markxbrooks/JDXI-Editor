""" bind texture array """
from OpenGL.raw.GL.ARB.internalformat_query2 import GL_TEXTURE_2D
from OpenGL.raw.GL.VERSION.GL_1_1 import glBindTexture
from OpenGL.raw.GL.VERSION.GL_1_3 import GL_TEXTURE0, glActiveTexture


def bind_texture_array(texture_id: int):
    """
    bind_texture_array

    :param texture_id:
    :return: None
    """
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, texture_id)
