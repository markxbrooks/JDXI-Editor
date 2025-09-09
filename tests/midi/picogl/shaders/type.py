from enum import Enum


class ShaderType(str, Enum):
    AXIS = "axis"
    ATOMS = "atoms"
    BONDS = "bonds"
    DEFAULT = "default"
    CALPHAS = "calphas"
    RIBBONS = "ribbons"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def get_name(self):
        return self.value

    def get_display_name(self):
        return self.value + "_shader"

    def vertex_path(self):
        return f"{self.value}_vert.glsl"

    def fragment_path(self):
        return f"{self.value}_frag.glsl"
