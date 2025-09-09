"""
Open GL shader_manager.current_shader_program compilation

"""

from typing import Optional

from picogl.backend.modern.core.shader.program import ShaderProgram
from picogl.logger import Logger as log

VERTEX_SHADER_SRC_HARDCODED_TEST = """#version 330 core

layout(location = 0) in vec3 in_position;
layout(location = 1) in vec3 in_color;

uniform mat4 mvp_matrix;
uniform float u_base_point_size;

out vec3 frag_color;

void main() {
    gl_Position = mvp_matrix * vec4(in_position, 1.0);
    frag_color = in_color;
    gl_PointSize = u_base_point_size;
}
"""


def compile_shaders(
    vertex_src: str, fragment_src: str, shader_name: Optional[str]
) -> Optional[ShaderProgram]:
    """
    Compiles and links a vertex + fragment shader_manager.current_shader_program shader_program using Qt's OpenGL API.

    :param shader_name: str
    :param vertex_src: Vertex shader_manager.current_shader_program GLSL code.
    :param fragment_src: Fragment shader_manager.current_shader_program GLSL code.
    :return: Linked PicoGLShader or None on failure.
    """

    picogl_program = ShaderProgram(shader_name=shader_name)
    picogl_program.init_shader_from_glsl(vertex_src, fragment_src)
    return picogl_program


def _log_shader_preview(vertex_src: str, fragment_src: str, preview_len: int = 200):
    """
    _log_shader_preview

    :param vertex_src: str
    :param fragment_src: str
    :param preview_len: int
    :return:
    """
    log.message(f"📄 Vertex Shader Preview:\n{vertex_src[:preview_len]}...")
    log.message(f"📄 Fragment Shader Preview:\n{fragment_src[:preview_len]}...")
