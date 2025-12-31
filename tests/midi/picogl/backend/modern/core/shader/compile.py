from OpenGL import GL as gl

from picogl.backend.modern.core.shader.helpers import log_gl_error


def compile_shader(shader_program: int, shader_type: int, source: str):
    """
    compile_vertex_shader

    :param shader_program: int shader program
    :param shader_type: int shader type e.g. GL_VERTEX_SHADER GL_FRAGMENT_SHADER
    :param source: shader source string
    """
    shader = gl.glCreateShader(shader_type)  # pylint: disable=E1111
    gl.glShaderSource(shader, source)
    gl.glCompileShader(shader)
    if gl.GL_TRUE != gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS):
        err = gl.glGetShaderInfoLog(shader)
        raise Exception(err)
    gl.glAttachShader(shader_program, shader)
    log_gl_error()
    return shader
