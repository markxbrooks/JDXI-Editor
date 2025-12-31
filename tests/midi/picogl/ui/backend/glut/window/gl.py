"""
Glut Window
"""

import sys

import OpenGL.GL as GL
import OpenGL.GLU as GLU
import OpenGL.GLUT as GLUT

from picogl.ui.abc_window import AbstractGLWindow


class GLWindow(AbstractGLWindow):

    def __init__(self, title: str = "window", *args, **kwargs):
        """__init__"""
        super().__init__()
        self.window = None
        self.width = None
        self.height = None
        self.title = title
        self.init_glut()
        self.controller = None
        self.update_if = GLUT.glutPostRedisplay

    def init_glut(self):
        """init_glut"""
        GLUT.glutInit(sys.argv)
        GLUT.glutInitDisplayMode(GLUT.GLUT_RGBA | GLUT.GLUT_DOUBLE | GLUT.GLUT_DEPTH)
        GLUT.glutInitWindowSize(800, 480)
        if self.title is not None:
            title_bytes = self.title.encode("utf-8")
        else:
            title_bytes = b"Window Title"
        self.window = GLUT.glutCreateWindow(title_bytes)
        GLUT.glutDisplayFunc(self.display)
        GLUT.glutReshapeFunc(self.resizeGL)
        GLUT.glutKeyboardFunc(self.on_keyboard)
        GLUT.glutSpecialFunc(self.on_special_key)
        GLUT.glutMouseFunc(self.mousePressEvent)
        GLUT.glutMotionFunc(self.mouseMoveEvent)
        GLUT.glutMouseWheelFunc(self.wheelEvent)

    def initializeGL(self):
        """initialize_gl"""
        GL.glClearColor(0.0, 0, 0.4, 0)
        GL.glDepthFunc(GL.GL_LESS)
        GL.glEnable(GL.GL_DEPTH_TEST)

    def paintGL(self):
        """paintGL"""
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GLU.gluLookAt(4.0, 3.0, -3.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        # built in model_matrix
        GLUT.glutSolidTeapot(1)
        print("please override paintGL")

    def update(self):
        """draw"""
        GLUT.glutPostRedisplay()

    def display(self):
        """display"""
        self.paintGL()
        GLUT.glutSwapBuffers()

    def idle(self):
        """idle"""
        pass

    def resizeGL(self, width: int, height: int):
        """resize"""
        print("please override resize")
        self.width = width
        self.height = height
        GL.glViewport(0, 0, width, height)
        GLU.gluPerspective(45.0, float(width) / float(height), 0.1, 1000.0)

    def on_keyboard(self, key, x, y):
        """on_keyboard"""
        if self.controller is not None:
            self.controller.on_keyboard(key, x, y)
        else:
            print("please overrider on_keyboard")

    def on_special_key(self, key, x, y):
        """on_special_key"""
        if self.controller is not None:
            self.controller.on_special_key(key, x, y)
        else:
            print("please overrider on_keyboard")

    def mousePressEvent(self, *args, **kwargs):
        """on_mouse"""
        if self.controller is not None:
            self.controller.mousePressEvent(*args, **kwargs)
        else:
            print("please overrider on_mouse")

    def mouseMoveEvent(self, *args, **kwargs):
        """on_mousemove"""
        if self.controller is not None:
            self.controller.mouseMoveEvent(*args, **kwargs)
        else:
            print("please overrider on_mousemove")

    def run(self):
        """run"""
        GLUT.glutMainLoop()


if __name__ == "__main__":

    win = GLWindow()
    win.run()
