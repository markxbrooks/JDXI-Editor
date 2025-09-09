import numpy as np
from OpenGL.raw.GL.VERSION.GL_1_0 import glViewport
from pyglm import glm

from picogl.logger import Logger as log
from picogl.logger import setup_logging
from picogl.renderer import GLContext
from picogl.ui.backend.glut.window.gl import GLWindow
from picogl.utils.gl_init import execute_gl_tasks, init_gl_list, paint_gl_list


class GlutRendererWindow(GLWindow):
    """Glut Rendered Window"""

    def __init__(self, width, height, title: str = None, context: GLContext = None, *args, **kwargs):
        super().__init__(title=title, *args, **kwargs)
        self.context = GLContext() if context is None else context
        self.title = title
        self.renderer = None
        self.width = width
        self.height = height
        # Mouse interaction state
        self.last_mouse_x = None
        self.last_mouse_y = None
        self.rotation_x = 0.0
        self.rotation_y = 0.0
        setup_logging()
        self.zoom_fov: int = 45 # field of view
        self.zoom_distance: int = 10 # camera backwards in Z
        self.distance_threshold: float = 5.0

    def initializeGL(self):
        """Initial OpenGL configuration."""
        log.message("Initializing OpenGL context...")
        execute_gl_tasks(init_gl_list)
        self.renderer.initialize_shaders()
        self.renderer.initialize_buffers()

    def calculate_mvp_matrix(self, width: int = 1920, height: int = 1080):
        """ calculate_mvp_matrix """
        self.context.projection = glm.perspective(
            glm.radians(self.zoom_fov), float(width) / float(height), 0.1, 1000.0
        )
        self.context.eye = glm.vec3(4, 3, self.zoom_distance)
        self.context.center = glm.vec3(0, 0, 0)
        self.context.up = glm.vec3(0, 1, 0)

        self.context.view = glm.lookAt(self.context.eye, self.context.center, self.context.up)
        self.context.model_matrix = glm.mat4(1.0)

        # The camera position in world space is just the eye
        self.context.eye_np = np.array(self.context.eye.to_list(), dtype=np.float32)

        self.context.mvp_matrix = (
                self.context.projection * self.context.view * self.context.model_matrix
        )

    def resizeGL(self, width, height):
        """resizeGL"""
        log.message(f"Resizing viewport to {width}x{height}...")
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)
        self.calculate_mvp_matrix(width, height)

    def paintGL(self):
        """paintGL"""
        execute_gl_tasks(paint_gl_list)
        self.renderer.render()

    def update_mvp(self):
        """Base perspective matrix from your existing method"""
        width, height = self.get_size()
        self.calculate_mvp_matrix(width, height)
        # Apply rotations
        rotation_matrix = glm.rotate(
            glm.mat4(1.0), glm.radians(self.rotation_x), glm.vec3(1, 0, 0)
        )
        rotation_matrix = glm.rotate(
            rotation_matrix, glm.radians(self.rotation_y), glm.vec3(0, 1, 0)
        )
        self.context.mvp_matrix = self.context.mvp_matrix * rotation_matrix
        self.update()  # Trigger repaint

    def mousePressEvent(self, button, state, x, y):
        """mousePressEvent"""
        if state == 0:  # Mouse button pressed
            self.last_mouse_x = x
            self.last_mouse_y = y

    def mouseMoveEvent(self, x, y):
        """ mouseMoveEvent """
        if self.last_mouse_x is not None and self.last_mouse_y is not None:
            dx = x - self.last_mouse_x
            dy = y - self.last_mouse_y
            # Adjust sensitivity as needed
            self.rotation_x += dy * 0.5
            self.rotation_y += dx * 0.5
            self.update_mvp()
        self.last_mouse_x = x
        self.last_mouse_y = y

    def wheelEvent(self, wheel=0, direction=0, x=0, y=0):
        """
        Mouse wheel zoom: adjusts distance if far, FOV if close.
        Positive direction -> zoom in, Negative -> zoom out.
        """
        zoom_step = direction * 0.5

        if self.zoom_distance > self.distance_threshold:
            # Distance zoom
            self.zoom_distance = max(1.0, self.zoom_distance - zoom_step)
        else:
            # FOV zoom
            self.zoom_fov = max(10.0, min(90.0, self.zoom_fov - zoom_step))
        print(f"Zoom mode: {'distance' if self.zoom_distance > self.distance_threshold else 'fov'} "
              f"| Distance: {self.zoom_distance:.2f} | FOV: {self.zoom_fov:.2f}")
        self.update_mvp()

    def get_size(self):
        return self.width, self.height


if __name__ == "__main__":

    win = GlutRendererWindow(width=1024, height=768)
    win.run()
