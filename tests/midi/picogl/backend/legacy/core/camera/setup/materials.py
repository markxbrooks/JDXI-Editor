"""
Setup Materials
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_AMBIENT_AND_DIFFUSE,
                                          GL_COLOR_MATERIAL, GL_DIFFUSE,
                                          GL_FRONT_AND_BACK, GL_SHININESS,
                                          GL_SPECULAR, glColorMaterial,
                                          glEnable, glMaterialf, glMaterialfv)


def setup_materials() -> None:
    """
    setup_materials

    :return: None
    """
    # Material settings
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50.0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
