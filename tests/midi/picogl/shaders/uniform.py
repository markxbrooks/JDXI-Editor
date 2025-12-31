from OpenGL.GL import glGetUniformLocation


def get_pgl_shader_uniform_location(shader, uniform_name: str) -> int:
    """
    get uniform location
    :param shader: PicoGL shader object
    :param uniform_name: string uniform name\
    :return: uniform location int
    """
    return glGetUniformLocation(shader.program, uniform_name)


def get_uniform_location(shader_program: int, uniform_name: str) -> int:
    """
    get_uniform_location

    :param shader_program: int
    :param uniform_name: str Name of the uniform
    :return: int
    """
    mvp_id = glGetUniformLocation(shader_program, uniform_name)
    return mvp_id
