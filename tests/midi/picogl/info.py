""" get gl information for printing"""
from OpenGL.GL import glGetString
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_RENDERER, GL_VENDOR, GL_VERSION
from OpenGL.raw.GL.VERSION.GL_2_0 import GL_SHADING_LANGUAGE_VERSION


def get_gl_info():
    """Get picogl info"""
    info = """
        Vendor: {0}
        RendererBase: {1}
        OpenGL Version: {2}
        Shader Version: {3}
        """.format(
        glGetString(GL_VENDOR).decode(),
        glGetString(GL_RENDERER).decode(),
        glGetString(GL_VERSION).decode(),
        glGetString(GL_SHADING_LANGUAGE_VERSION).decode(),
    )
    return info
