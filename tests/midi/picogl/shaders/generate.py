from typing import Optional

from picogl.backend.modern.core.shader.program import ShaderProgram
from picogl.logger import Logger as log
from picogl.shaders.compile import compile_shaders


def generate_shader_programs(
    vertex_shader_src: str, fragment_shader_src: str, shader_name: str = "default"
) -> Optional[ShaderProgram]:
    """
    generate_shader_programs

    :param vertex_shader_src: str
    :param fragment_shader_src: str
    :param shader_name: str
    :return: tuple[PicoGLShader, GluInt]
    """
    picogl_shader_program = compile_shaders(
        vertex_shader_src, fragment_shader_src, shader_name
    )
    if picogl_shader_program is None:
        return None
    shader_program = (
        picogl_shader_program.program_id()
    )  # ✅ This is safe for glUseProgram
    if shader_program is None:
        log.error(
            "❌ Shader shader_program could not be created. Aborting scene initialization."
        )
        return None
    return picogl_shader_program
