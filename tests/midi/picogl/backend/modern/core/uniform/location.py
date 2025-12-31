from OpenGL.GL import glGetUniformLocation


def get_uniform_location(shader_program: int, uniform_name: str) -> int:
    """
    get_uniform_location

    :param shader_program: int
    :param uniform_name: str
    :return: int
    """
    location = glGetUniformLocation(shader_program, uniform_name)
    return location
