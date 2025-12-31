def enable_points_rendering_state() -> None:
    """
    enable_points_rendering_state

    :return: None
    """
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_PROGRAM_POINT_SIZE)
    glEnable(GL_POINT_SPRITE)
    glEnable(GL_PROGRAM_POINT_SIZE)
    glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)
