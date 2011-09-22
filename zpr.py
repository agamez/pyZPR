#!/usr/bin/python
from OpenGL import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import numpy
from numpy import matrix
from numpy import array
from numpy import cross
from numpy.linalg import norm, det

import sys
from math import pi, sin, cos, tan, radians, sqrt

class Mouse():
    def __init__(self):
        self.rotate = False
        self.pan = False
        self.zoom = False
        self.old_mpos = {'x': 0.0, 'y': 0.0}
        self.dx = 0.0
        self.dy = 0.0

    def click(self, button, state, x, y):
        self.rotate = False
        self.pan = False
        self.zoom = False

        if state == GLUT_DOWN:

            if button == GLUT_LEFT_BUTTON: self.pan = True 
            if button == GLUT_MIDDLE_BUTTON: self.rotate = True 
            if button == GLUT_RIGHT_BUTTON: self.zoom = True
        
        self.old_mpos = {'x': float(x), 'y': float(y)}

    def motion(self, x, y):
        self.dx = float(x)-self.old_mpos['x']
        self.dy = float(y)-self.old_mpos['y']

        self.old_mpos = {'x': float(x), 'y': float(y)}

class Keyboard():
    def __init__(self):
        self.left = False
        self.right = False
        self.forward = False
        self.backward = False
        
        self.up = False
        self.down = False
        
        self.rleft = False
        self.rright = False

    def keydown(self, key, x, y):
        self.left = False
        self.right = False
        self.forward = False
        self.backward = False

        self.up = False
        self.down = False

        if key == 'a':
            self.left = True
        elif key == 'd':
            self.right = True
        elif key == 'w':
            self.forward = True
        elif key == 's':
            self.backward = True
        elif key == GLUT_KEY_UP:
            self.up = True
        elif key == GLUT_KEY_DOWN:
            self.down = True
        elif key == GLUT_KEY_LEFT:
            self.rleft = True
        elif key == GLUT_KEY_RIGHT:
            self.rright = True
    
    def keyup(self, key, x, y):
        if key == 'a':
            self.left = False
        elif key == 'd':
            self.right = False
        elif key == 'w':
            self.forward = False
        elif key == 's':
            self.backward = False
        elif key == GLUT_KEY_UP:
            self.up = False
        elif key == GLUT_KEY_DOWN:
            self.down = False
        elif key == GLUT_KEY_LEFT:
            self.rleft = False
        elif key == GLUT_KEY_RIGHT:
            self.rright = False
        


class Screen:
    def __initLights__(self):
        glutSetWindow(self.id)
        light0Position = [0, 0, 1, 0]
        light0Color = array([1, 1, 1, 0])*1

        glLightfv(GL_LIGHT0,  GL_POSITION,  light0Position)
        glLightfv(GL_LIGHT0,  GL_AMBIENT,  (0.4*light0Color).tolist())
        glLightfv(GL_LIGHT0,  GL_DIFFUSE,  (0.8*light0Color).tolist())
        glLightfv(GL_LIGHT0,  GL_SPECULAR, (0.9*light0Color).tolist())

        glLightf(GL_LIGHT0,  GL_CONSTANT_ATTENUATION,  0.1)
        glLightf(GL_LIGHT0,  GL_LINEAR_ATTENUATION,  0.05)

        glMaterialfv(GL_FRONT, GL_SHININESS, 100)
        
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)

    def __initKeybMouse__(self):
        def motion(*args):
            self.mouse.motion(*args)
            glutPostRedisplay()
        def press(*args):
            self.keyboard.keydown(*args)
            glutPostRedisplay()

        glutSetWindow(self.id)

        self.mouse = Mouse()
        glutMouseFunc(self.mouse.click)
        glutMotionFunc(motion)

        self.keyboard = Keyboard()
        glutKeyboardFunc(press)
        glutKeyboardUpFunc(self.keyboard.keyup)
        glutSpecialFunc(press)
        glutSpecialUpFunc(self.keyboard.keyup)

    def __init__(self, name):
        self.fovy = 20
        self.zNear = 1000
        self.zFar =  1000000

        self.eye = matrix([-5000.0, 0.0, 1000.0])
        self.center = matrix([0.0, 0.0, 1000.0])
        self.up = matrix([0.0, 0.0, 1.0])

        self.width=450.0
        self.height=450.0

        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        self.id = glutCreateWindow(name)

        glClearColor(1, 1, 1, 1)

        glShadeModel(GL_SMOOTH)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_ONE_MINUS_SRC_ALPHA, GL_SRC_ALPHA)
        
        self.__initLights__()  
        self.__initKeybMouse__()

        glutReshapeFunc(self.reshape)
        glutDisplayFunc(self.display)

    def axis(self):
        m = cross(self.up, self.center - self.eye)
        return (self.up, m/norm(m))

    def reshape(self, width, height):
        self.width=float(width)
        self.height=float(height)

        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fovy, self.width/self.height, self.zNear, self.zFar)
        glMatrixMode(GL_MODELVIEW)

    @staticmethod
    def rotatePoint(p, o, d, a):
        c = cos(a)
        cs_1 = 1.0-c
        s = sin(a)

        dL = d.tolist()[0]
        M1 = array([dL, dL, dL])
        M2 = M1.transpose()

        Ms = array([[+c,       -dL[2]*s, +dL[1]*s],
                    [+dL[2]*s, +c,       -dL[0]*s],
                    [-dL[1]*s, +dL[0]*s, +c]])
        M = M1*M2*cs_1 + Ms

        ret = o + ( M * ((p-o).transpose()) ).transpose()
        return ret

    def rotate(self, dx, dy):
        dirc = self.axis()
        self.eye = Screen.rotatePoint(self.eye, self.center, dirc[0], -dx*pi)
        self.eye = Screen.rotatePoint(self.eye, self.center, dirc[1], dy*pi)

        self.up = Screen.rotatePoint(self.center+self.up, self.center, dirc[0], -dx*pi) - self.center
        self.up = Screen.rotatePoint(self.center+self.up, self.center, dirc[1], dy*pi) - self.center
        self.up = self.up / norm(self.up)
    
    def rotate_camera(self, dx, dy):
        dirc = self.axis()
        self.center = Screen.rotatePoint(self.center, self.eye, dirc[0], -dx*pi)
        self.center = Screen.rotatePoint(self.center, self.eye, dirc[1], dy*pi)

        self.up = Screen.rotatePoint(self.center+self.up, self.center, dirc[0], -dx*pi) - self.center
        self.up = Screen.rotatePoint(self.center+self.up, self.center, dirc[1], dy*pi) - self.center
        self.up = self.up / norm(self.up)

    def zoom(self, dx, dy):
        self.eye += 5*dy*(self.center-self.eye)

    def pan(self, dx, dy):
        dirc = self.axis()
        length = tan(radians(self.fovy/2)) * norm(self.eye - self.center) * 2
        self.center = self.center + ( dirc[0]*dy + dirc[1]*dx ) * length
    
    def move(self, dd, dirc):
        dirc = dirc/norm(dirc)
        self.center += dd*dirc
        self.eye += dd*dirc


    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        if self.mouse.rotate:
            self.rotate(self.mouse.dx/self.width, self.mouse.dy/self.height)
        if self.mouse.zoom:
            self.zoom(self.mouse.dx/self.width, self.mouse.dy/self.height)
        if self.mouse.pan:
            self.pan(self.mouse.dx/self.width, self.mouse.dy/self.height)

        if self.keyboard.left:
            self.move(-200, cross(self.center-self.eye, self.up))
        if self.keyboard.right:
            self.move(200, cross(self.center-self.eye, self.up))
        if self.keyboard.forward:
            self.move(200, self.center-self.eye)
        if self.keyboard.backward:
            self.move(-200, self.center-self.eye)
        
        if self.keyboard.up:
            self.move(50, self.up)
        if self.keyboard.down:
            self.move(-50, self.up)
        
        if self.keyboard.rleft:
            self.rotate_camera(-0.001*pi, 0)
        if self.keyboard.rright:
            self.rotate_camera(0.001*pi, 0)
        

        camera = self.eye.tolist()[0] + self.center.tolist()[0] + self.up.tolist()[0]
        gluLookAt(*camera)

        if self.displayFunc:
            self.displayFunc()

        glutSwapBuffers()

        return

def displayAxis():
    glPushMatrix()
    glPushName(0)
    glColor3f(0.3,0.3,0.3)
    glutSolidSphere(0.7, 20, 20)
    glPopName()
    glPopMatrix()

    glPushMatrix()
    glPushName(1)
    glColor3f(1,0,0)
    glRotatef(90,0,1,0)
    glutSolidCone(0.6, 4.0, 20, 20)
    glPopName()
    glPopMatrix()
    
    glPushMatrix()
    glPushName(2)
    glColor3f(0,0,1)
    glRotatef(-90,1,0,0)
    glutSolidCone(0.6, 4.0, 20, 20)
    glPopName()
    glPopMatrix()
    
    glPushMatrix()
    glPushName(3)
    glColor3f(0,1,0)
    glutSolidCone(0.6, 4.0, 20, 20)
    glPopName()
    glPopMatrix()
    



def main():
    screen = Screen('Prueba')
    screen.displayFunc = displayAxis

    glutMainLoop()

    return


if __name__ == '__main__':
    main()
