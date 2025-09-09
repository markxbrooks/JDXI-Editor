"""
Setup lighting
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_AMBIENT, GL_COLOR_BUFFER_BIT,
                                          GL_DEPTH_BUFFER_BIT, GL_DIFFUSE,
                                          GL_FOG, GL_FOG_COLOR, GL_FOG_END,
                                          GL_FOG_MODE, GL_FOG_START,
                                          GL_FRONT_AND_BACK, GL_LIGHT0,
                                          GL_LIGHT1, GL_LIGHT2, GL_LIGHT3,
                                          GL_LIGHT4, GL_LIGHTING, GL_LINEAR,
                                          GL_MODELVIEW, GL_POSITION,
                                          GL_SHININESS, GL_SPECULAR,
                                          GL_UNPACK_ALIGNMENT, glClear,
                                          glClearColor, glDisable, glEnable,
                                          glFogf, glFogfv, glFogi, glLightfv,
                                          glLoadIdentity, glMaterialf,
                                          glMatrixMode, glPixelStorei,
                                          glPopMatrix, glPushMatrix)


def set_fog_state(
    fog_state: bool,
    fog_density_value: float,
    fog_start_value: float,
    fog_end_value: float,
) -> None:
    """
    set_fog_state

    :param fog_density_value: float
    :param fog_end_value: float
    :param fog_start_value: float
    :param fog_state: bool
    :return: None
    """
    if fog_start_value >= fog_end_value:
        fog_start_value = fog_end_value - 1
    fog_density_value = min(0.3, fog_density_value)
    if fog_state:
        glEnable(GL_FOG)
        glFogfv(
            GL_FOG_COLOR,
            [
                fog_density_value,
                fog_density_value,
                fog_density_value,
                fog_density_value,
            ],
        )
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogf(GL_FOG_START, fog_start_value)
        glFogf(GL_FOG_END, fog_end_value)
    else:
        glDisable(GL_FOG)


def set_second_light_state(second_light_state: bool) -> None:
    """
    set_second_light_state

    :param second_light_state: bool Whether the second light is on or off
    :return: None

    Second light
    """
    if second_light_state:
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_POSITION, [-10.0, -10.0, -10.0, 1.0])
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.5, 0.5, 0.5, 1.0])
        glLightfv(GL_LIGHT1, GL_SPECULAR, [0.3, 0.3, 0.3, 1.0])
        glEnable(GL_LIGHT2)
        glLightfv(GL_LIGHT2, GL_POSITION, [90.0, 90.0, 90.0, 1.0])
        glLightfv(GL_LIGHT2, GL_DIFFUSE, [0.5, 0.5, 0.5, 1.0])
        glLightfv(GL_LIGHT2, GL_SPECULAR, [0.3, 0.3, 0.3, 1.0])
        glEnable(GL_LIGHT3)
        glLightfv(GL_LIGHT3, GL_POSITION, [-90.0, -90.0, -90.0, 1.0])
        glLightfv(GL_LIGHT3, GL_DIFFUSE, [0.5, 0.5, 0.5, 1.0])
        glLightfv(GL_LIGHT3, GL_SPECULAR, [0.3, 0.3, 0.3, 1.0])
        glEnable(GL_LIGHT4)
        glLightfv(GL_LIGHT4, GL_POSITION, [270.0, 270.0, 270.0, 1.0])
        glLightfv(GL_LIGHT4, GL_DIFFUSE, [0.5, 0.5, 0.5, 1.0])
        glLightfv(GL_LIGHT4, GL_SPECULAR, [0.3, 0.3, 0.3, 1.0])
    else:
        glDisable(GL_LIGHT1)


def set_background_color(show_white_background: bool) -> None:
    """
    set_background_color

    :param show_white_background: bool
    :return: None
    Choose bg color_array
    """
    if show_white_background:
        glClearColor(1.0, 1.0, 1.0, 1.0)  # White background
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Black
    else:
        glClearColor(0.0, 0.0, 0.0, 1.0)


def setup_lighting(mode: int = 0) -> None:
    """
    setup_lighting

    :param mode: int lighting gl_mode
    :return: None
    """
    current_shininess = 1.0
    if mode == 0:
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        # glEnable(GL_COLOR_MATERIAL)
        # Set up light position_array (in eye space)
        light_pos = [10.0, 10.0, 10.0, 1.0]  # positional black light
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        # Set light color_array
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 128.0 * current_shininess)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    if mode == 2:
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        # Set up light position_array (in eye space)
        light_pos = [0.0, 0.0, 0.0, 1.0]  # positional light
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        # Set light color_array
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    elif mode == 1:
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()  # reset modelview matrix

        # Set light position_array (camera-relative)
        light_pos = [10.0, 10.0, 10.0, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)

        glPopMatrix()

        # Set light properties (these are not affected by the matrix)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    elif mode == 3:
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        # Set light properties (independent of matrix)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])

        # Call this *after* your model_matrix/view transforms (e.g., after gl_update_camera_matrix)
        light_pos = [
            10.0,
            10.0,
            10.0,
            1.0,
        ]  # Positional light, relative to object/world
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
