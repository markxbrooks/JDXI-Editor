"""
ShaderRegistry
==============

Example Usage:
==============
>>>shader_registry = ShaderRegistry()
...# Load src at app start
...for shader_type_value in ShaderType:
...   shader_registry.load_and_add(shader_type_value)
...
...# Later...
...shader_manager.current_shader_program = shader_registry.get(ShaderType.ATOMS)
...if shader_manager.current_shader_program:
...    shader_manager.current_shader_program.bind()
...


File naming convention:
=======================
Ensure GLSL files follow the naming pattern:

atoms_vert.glsl
atoms_frag.glsl
bonds_vert.glsl
bonds_frag.glsl
"""

from dataclasses import dataclass, field
from typing import Dict, Optional

from picogl.backend.modern.core.shader.load import load_shader
from picogl.backend.modern.core.shader.program import ShaderProgram
from picogl.logger import Logger as log
from picogl.shaders.type import ShaderType


@dataclass
class ShaderRegistry:
    """ShaderRegistry"""

    shaders: Dict[ShaderType, ShaderProgram] = field(default_factory=dict)

    def load_and_add(self, shader_type: ShaderType) -> Optional[ShaderProgram]:
        """
        Load, compile, and register a shader_manager.current_shader_program for the given ShaderType.
        """
        try:
            vertex_src = load_shader(shader_type.vertex_path())
            fragment_src = load_shader(shader_type.fragment_path())
            program = qt_compile_shaders(vertex_src, fragment_src)
            if program:
                self.shaders[shader_type] = program
            return program
        except Exception as ex:
            log.error(
                f"❌ Failed to load shader_manager.current_shader_program {shader_type}: {ex}"
            )
            return None

    def get(self, shader_type: ShaderType) -> Optional[ShaderProgram]:
        return self.shaders.get(shader_type)

    def has(self, shader_type: ShaderType) -> bool:
        return shader_type in self.shaders

    def release_all(self):
        for shader_type, shader in self.shaders.items():
            if hasattr(shader, "release") and callable(shader.release):
                try:
                    shader.release()
                except Exception as e:
                    log.warning(
                        f"⚠️ Failed to release shader_manager.current_shader_program '{shader_type}': {e}"
                    )
        self.shaders.clear()
