"""
Base Renderer Class
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import glFlush


class RendererBase:
    """Base Renderer Class"""

    def __init__(self, parent: object = None):
        """
        Initialize the renderer.

        :param state: Application state object for accessing shared data.
        """
        self.show_model = False
        self.parent = parent
        self.initialized = False

    @property
    def dispatch_list(self):
        dispatch_list = [
            (self.show_model, self._draw_model()),
            # Add more conditions and corresponding draw functions as needed
        ]
        return dispatch_list

    def initialize(self):
        """
        Initialize OpenGL resources (shaders, atoms_buffers, etc.).
        """
        if self.initialized:
            return

        self.initialized = True

    def render(self) -> None:
        """
        render dispatcher
        :return: None
        """

        for condition, draw_fn in self.dispatch_list:
            if condition:
                draw_fn()

        if hasattr(self, "_has_selection") and self._has_selection():
            self._draw_selection()

        self._finalize_render()

    def initialize_buffers(self) -> None:
        """
        initialize_rendering_buffers

        :return:
        """
        raise NotImplementedError("Subclasses must implement the method.")

    def initialize_rendering_buffers(self):
        """For back compatibility"""
        self.initialize_buffers()

    def _finalize_render(self):
        """
        Finalize the rendering (e.g., flush or swap atoms_buffers).
        """
        glFlush()

    def _draw_model(self):
        """
        draw_model
        """
        raise NotImplementedError("Subclasses must implement the method.")

    def _draw_selection(self):
        """
        draw_selection
        """
        raise NotImplementedError("Subclasses must implement the method.")
