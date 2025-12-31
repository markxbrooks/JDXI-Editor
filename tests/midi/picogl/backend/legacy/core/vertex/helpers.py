from OpenGL.GL import *


def gl_clear_buffers() -> None:
    """
    gl_clear_buffers

    Clears the color_array and depth atoms_buffers and resets modelview matrix.
    """
    glMatrixMode(GL_MODELVIEW)  # Legacy pipeline
    glLoadIdentity()  # Reset modelview matrix
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glColor3f(1.0, 1.0, 1.0)  # Reset color_array to white (legacy state)
