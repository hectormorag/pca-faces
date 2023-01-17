import os, sys, math, pdb

# PyQt5 libraries
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt, QEvent, QObject, pyqtSignal, pyqtProperty, pyqtSlot, QPoint, QSize, QThread, QThreadPool
from PyQt5.QtOpenGL import QGL, QGLWidget
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, qApp, QFileDialog, QHBoxLayout, QOpenGLWidget, \
    QSlider, QWidget, QMessageBox
from PyQt5.QtGui import QColor, QIcon

# OpenGL libraries (pip install pyOpenGL pyOpenGL-accelerate)
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GL import *
import OpenGL.GL as gl

# PIL libraries (pip install Pillow)
import PIL
from PIL import Image
from PIL import ImageChops

# numpy libraries
import numpy
from numpy import eye
import numpy as np

# scipy libraries
from scipy.misc import *
from scipy import linalg
from scipy.spatial import procrustes
import scipy.ndimage as spi

# imageio libraries (pip install imageio)
import imageio
from imageio.v2 import imsave
from imageio.v2 import imread

# matplotlib libraries
import matplotlib
import matplotlib.pyplot

# Import the class "Ui_MainWindow" from the file "GUI.py"
from GUI import Ui_MainWindow

# Import the class "OBJ" from the file "OBJ.py"
from OBJ import OBJ, OBJFastV

# Some global variables, to be able to use them anywhere and also to initialize them
InputModelLoaded = InputTextureLoaded = InputListCreated = False
InputTexturePath = []
InputTextureDim = 256
InputModel = TarModel = []
TargetModelLoaded = TargetTextureLoaded = TargetListCreated = False
TarTexturePath = []
Tx = Ty = 0
Tz = 1
r_mode = c_mode = "Faces"
bg_color = 0.0
LeftXRot = LeftYRot = 0
b_Ready = False
Updated = False
Root = {}
Tval = Gval = 0
P_Tval = P_Gval = 0
b_ProcessDone = b_Process2Done = b_Ready = PCA_done = False
old_Gval = old_Tval = 0


####################################################################################################
# The Main Window (GUI) --- TASKS TO DO HERE
####################################################################################################
class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)  # The 2 lines here are always presented like this
        QMainWindow.__init__(self, parent)  # Just to initialize the window

        # All the elements from our GUI are added in "ui"
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Add a GLWidget (will be used to display our 3D object)
        self.glWidget = GLWidget()
        # Add the widget in "frame_horizontalLayout", an element from the GUI
        self.ui.frame_horizontalLayout.addWidget(self.glWidget)

        # Update Widgets
        # Connect a signal "updated" between the GLWidget and the GUI, just to have a link between the 2 classes
        self.glWidget.updated.connect(self.updateFrame)

        # RadioButton (Rendering Mode)
        # Connect the radiobutton to the function on_rendering_button_toggled
        self.ui.rbFaces.toggled.connect(self.rendering_button_toggled)
        # It will be used to switch between 2 modes, full/solid model or cloud of points
        self.ui.rbPoints.toggled.connect(self.rendering_button_toggled)

        # RadioButton (Background Color)
        # Connect the radiobutton to the function on_bgcolor_button_toggled
        self.ui.rbWhite.toggled.connect(self.bgcolor_button_toggled)
        # Just an example to change the background of the 3D frame
        self.ui.rbBlack.toggled.connect(self.bgcolor_button_toggled)

        # Buttons
        # Connect the button to the function LoadFileClicked (will read the 3D file)
        self.ui.LoadFile.clicked.connect(self.LoadFileClicked)
        # Connect the button to the function ProcessClicked (will process PCA)
        self.ui.Process.clicked.connect(self.ProcessClicked)
        # Connect the button to the function SaveOBJ (will write a 3D file)
        self.ui.exportResult.clicked.connect(self.SaveOBJ)

        # Sliders
        # Connect the slider to the function T_SliderValueChange
        self.ui.Tslider.valueChanged.connect(self.T_SliderValueChange)
        # Connect the slider to the function G_SliderValueChange
        self.ui.Gslider.valueChanged.connect(self.G_SliderValueChange)

        # Disable buttons/sliders
        self.ui.Tslider.setEnabled(False)
        self.ui.Gslider.setEnabled(False)

    def LoadFileClicked(self):
        global InputModel, InputModelLoaded, InputListCreated, InputTextureLoaded, InputTexturePath, FileNameWithExtension
        global TarModel, TarTexturePath, PCA_done
        try:
            # To display a popup window that will be used to select a file (.obj or .png)
            myFile = QFileDialog.getOpenFileName(None, 'OpenFile', "", "3D object(*.obj);;Texture(*.png)")
            myPath = myFile[0]
            # If the extension is .obj (or .png), will remove the 4 last characters (== the extension)
            GlobalNameWithoutExtension = myPath[:-4]
            FileNameWithExtension = QFileInfo(myFile[0]).fileName()  # Just the filename
            if myFile[0] == myFile[1] == '':
                # No file selected or cancel button clicked - so do nothing
                pass
            else:
                InputModel = TarModel = []
                InputModelLoaded = InputTextureLoaded = InputListCreated = False
                InputTexturePath = GlobalNameWithoutExtension + ".png"
                InputModel = OBJ(GlobalNameWithoutExtension + ".obj")  # Will use the class OBJ to read our 3D file

                imsave("TarTexture" + ".png", imread(InputTexturePath))
                TarTexturePath = '/'.join(myPath.split('/')[:-1]) + '/TarTexture.png'
                TarModel = InputModel
                # We read the 2 files, so we can now set the boolean value to True
                # (the GLWidget will now display it automatically if the 2 variables are used there)
                InputModelLoaded = InputTextureLoaded = True
                PCA_done = False
                self.glWidget.update()
        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
            print(myFile)
        except ValueError:
            print("Value Error.")
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

    def ProcessClicked(self):
        global b_ProcessDone, b_Process2Done, PCA_done

        # For the bonus task, you will need to call the thread instead of the function
        gThread = GeometryThreadClass()
        gThread.run()
        print("PCA TEX DONE")

        tThread = TextureThreadClass()
        tThread.run()
        print("PCA GEO DONE")

        gThread.stop()
        tThread.stop()

        # self.PCA_Tex()  # Run the function to do the PCA on textures
        # b_ProcessDone = True
        # print("PCA TEX DONE")

        # self.PCA_Geo()  # Run the function to do the PCA on vertices
        # b_Process2Done = True
        # print("PCA GEO DONE")

        PCA_done = True

        # Unlock and prepare sliders
        self.ui.Tslider.blockSignals(True)
        self.ui.Tslider.setValue(0)
        self.T_SliderValueChange(0)
        self.ui.Tslider.blockSignals(False)
        self.ui.Tslider.setEnabled(True)
        S = self.checkSign(Root['Tex']['WTex'][0], Root['Tex']['WTex'][1])
        self.ui.Tslider.setRange(int(S * Root['Tex']['WTex'][0]), int(S * Root['Tex']['WTex'][1]))

        self.ui.Gslider.blockSignals(True)
        self.ui.Gslider.setValue(0)
        self.G_SliderValueChange(0)
        self.ui.Gslider.blockSignals(False)
        self.ui.Gslider.setEnabled(True)
        T = self.checkSign(Root['models']['WGeo'][0], Root['models']['WGeo'][1])
        self.ui.Gslider.setRange(int(T * Root['models']['WGeo'][0]), int(T * Root['models']['WGeo'][1]))

    def PCA_Tex(self):
        global Root

        ###########################################
        # TASK 1 FOR THE ASSIGNMENT
        ###########################################

        ## Note: You will be evaluated on each task
        ## If it doesn't work, you will be evaluated on your efforts and the quality of the code by trying to do it

        ## Guideline: Read model1.png and model2.png
        ## Do the PCA with the 2 textures, similar to what we did in session 5

        ## >>> ADD CODE BELOW <<<


        # ....
        # the code is at thread
        pass


    def PCA_Geo(self):
        global Root, b_ProcessDone
        global OriModel, TarModel
        global Tval, Gval, b_Ready

        ###########################################
        # TASK 2 FOR THE ASSIGNMENT
        ###########################################

        ## Guideline: Read model1.obj and model2.obj with the "OBJFastV(...)" function to extract quickly the vertices
        ## Do the PCA with the vertices (drawing on the function PCA_Tex(), try to do the same but with the vertices)
        ## Or adapt the code

        ## >>> ADD CODE BELOW <<<

        # ....
        # the code is in thread
        pass



    def T_SliderValueChange(self, value):
        global Tval, Root, TarTexture, b_ProcessDone, b_Process2Done, P_Tval, Tval
        global TarTextureDim
        Tval = value

        ###########################################
        # TASK 3 FOR THE ASSIGNMENT
        ###########################################
        ## Texture slider ( PCA : Input Texture <----> Target Texture )
        if b_ProcessDone == True and b_Process2Done == True:
            ## You have to create the new texture by using the formula of the PCA
            ## As a reminder, Texture = Mean + W1 * E1 + W2 * E2 + ....
            ## Mean is: Root['Tex']['XmTex']
            ## W is: Tval  (weight is linked to the slider value "Tval")
            ## E is: Root['Tex']['VrTex'][0]
            ## The product Wi * Ei must be done using numpy.dot(value1, value2)

            ## >>> ADD CODE BELOW <<<            
            ## New target texture (1D array)
            N_TarTex = Root['Tex']['XmTex'] + numpy.dot(Tval, Root['Tex']['VrTex'][0])

            ## Reshape the variable N_TarTex to have the real texture 256*256*4 (RGBA) and use it as the new texture
            data = np.array(N_TarTex)
            TarTexture = data.reshape((256,256,4))
            
            imageio.v2.imsave("TarTexture" + ".png", TarTexture)

        self.ui.Tslider.blockSignals(True)
        self.ui.Tslider.setValue(value)
        P_Tval = str(Tval)
        self.ui.textinputtarget.setText(P_Tval)
        self.ui.Tslider.blockSignals(False)


    def G_SliderValueChange(self, value):
        global Gval, Root, OriModel, TarModel, b_ProcessDone, b_Process2Done, P_Gval, Gval
        Gval = value

        ###########################################
        # TASK 4 FOR THE ASSIGNMENT
        ###########################################

        ## Geometry slider ( model1 <----> model2 )
        if b_ProcessDone == True and b_Process2Done == True:
            ## You have to create the new geometry by using the formula of the PCA
            ## As a reminder, 3DFace = Mean + W1 * E1 + W2 * E2 + ....
            ## Mean is: Root['models']['XmGeo']
            ## W is: Gval  (weight is linked to the slider value "Gval")
            ## E is: Root['models']['VrGeo']
            ## The product W * E must be done using numpy.dot(value1, value2)


            ## >>> ADD CODE BELOW <<<
            ## New target geometry (1D array), use formula of the PCA the same way as for the texture
            N_TarModel = Root['models']['XmGeo'] + numpy.dot(Gval, Root['models']['VrGeo'][0])
            arr_3d = np.zeros((5904, 3))
            count = 0

            for x in range(5904):
                arr_3d[x][0] = N_TarModel[count]
                x += 1
                count += 1
            for y in range(5904):
                arr_3d[y][1] = N_TarModel[count]
                y += 1
                count += 1
            for z in range(5904):
                arr_3d[z][2] = N_TarModel[count]
                z += 1
                count += 1


            ## Concatenate x, y and z together (as a float)
            row = tmp = []
            for i in range(0, 5904):
                row = float(arr_3d[i][0]), float(arr_3d[i][1]), float(arr_3d[i][2])
                ##                 x                    y                    z
                tmp.append(row)

            InputModel.vertices = tmp  # TarModel.vertices is the new 3D model

        self.ui.Gslider.blockSignals(True)
        self.ui.Gslider.setValue(value)
        P_Gval = str(Gval)
        self.ui.textmodels.setText(P_Gval)
        self.ui.Gslider.blockSignals(False)


    def SaveOBJ(self):
        ###########################################
        # TASK 5 FOR THE ASSIGNMENT
        ###########################################

        ## Try to see how the OBJ class works (file OBJ.py)
        ## Instead of reading, you should now write in a file
        ## You will need to add everything in the .obj, not only vertices!

        ## Open the model1.obj with a text editor for example to see what you have in it
        ## The new file will be similar but with the new vertices (v)
        ## You can reuse the original file to add back vt, vn, f...

        ## >>> ADD CODE BELOW <<<

        # ....

        # pass
        obj_name = "savedObj"
        obj_name = obj_name + '.obj'

        mtl_name = obj_name.replace('.obj', '.mtl')
        
        # write obj
        with open(obj_name, 'w') as f:

            # follow format of wavefront obj
            line = "mtllib {}\n".format(os.path.abspath(mtl_name))
            f.write(line)
            line = 'o Face\n'
            f.write(line)
            line = 's 1\n'
            f.write(line)
            
            # vertices
            vertices = InputModel.vertices
            for i in range(len(vertices)):
                line = 'v {} {} {} \n'.format(vertices[i][0], vertices[i][1], vertices[i][2])
                f.write(line)

            # vt
            texcoords = InputModel.texcoords
            for i in range(len(texcoords)):
                line = 'vt {} {} \n'.format(texcoords[i][0], texcoords[i][1])
                f.write(line)

            # vn
            normals = InputModel.normals
            for i in range(len(normals)):
                line = 'vn {} {} {} \n'.format(normals[i][0], normals[i][1], normals[i][1])
                f.write(line)

            f.write("g Surf0\n")
            f.write("usemtl TarTexture\n")

            # write faces
            faces = InputModel.faces
            for i in range(len(faces)):
                line = 'f {}/{}/{} {}/{}/{} {}/{}/{} \n'.format(faces[i][0][0],faces[i][1][0],faces[i][2][0], faces[i][0][1], faces[i][1][1], faces[i][2][1], faces[i][0][2],faces[i][1][2], faces[i][2][2])
                f.write(line)


    def checkSign(self, W1, W2):
        ## Check the weight, to know which one is negative/positive
        ## Important for the sliders to have the - on the left and + on the right
        if W1 < 0:
            res = 1
        else:
            res = -1
        return res

    def rendering_button_toggled(self):
        global r_mode, Updated
        radiobutton = self.sender()

        if radiobutton.isChecked():
            r_mode = radiobutton.text()  # Save "Faces" or "Points" in r_mode
        Updated = True
        self.glWidget.update()

    def bgcolor_button_toggled(self):
        global bg_color
        radiobutton = self.sender()  # Catch the click
        if radiobutton.isChecked():  # Will check which button is checked
            # Will store and use the text of the radiobutton
            # to store a value in the variable "bg_color" that will be used in the GLWidget
            color = radiobutton.text()
            if color == "White":
                bg_color = 1.0
            elif color == "Black":
                bg_color = 0.0

    def updateFrame(self):
        self.glWidget.update()

####################################################################################################
# The OpenGL Widget --- it's normally not needed to touch this part especially paintGL
####################################################################################################
class GLWidget(QGLWidget):
    updated = pyqtSignal(int)  # pyqtSignal is used to allow the GUI and the OpenGL widget to sync
    xRotationChanged = pyqtSignal(int)
    yRotationChanged = pyqtSignal(int)
    zRotationChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        self.lastPos = QPoint()

    def initializeGL(self):
        glEnable(GL_TEXTURE_2D)
        self.tex = glGenTextures(1)

    def paintGL(self):
        global InputModel, InputModelLoaded, InputTextureLoaded, InputListCreated
        global TarModel, TargetModelLoaded, TargetTextureLoaded, TargetListCreated
        global c_mode, bg_color, FileNameWithExtension, Tx, Ty, Tz, Updated
        global old_Gval, Gval, old_Tval, Tval
        TarTexture = ""

        # IF we have nothing to display, no model loaded: just a default background with axis
        if InputModelLoaded == False:

            glClearColor(bg_color, bg_color, bg_color, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()  # identity matrix, resets the matrix back to its default state

            # field of view (angle), ratio, near plane, far plane, all values must be > 0
            gluPerspective(60, 1, 0.01, 10000)

            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            glTranslate(Tx, Ty, -Tz)

            glRotated(self.xRot / 16, 1.0, 0.0, 0.0)
            glRotated(self.yRot / 16, 0.0, 1.0, 0.0)
            glRotated(self.zRot / 16, 0.0, 0.0, 1.0)

            self.qglColor(Qt.red)
            self.renderText(10, 20, "X")
            self.qglColor(Qt.green)
            self.renderText(10, 40, "Y")
            self.qglColor(Qt.blue)
            self.renderText(10, 60, "Z")

            glLineWidth(2.0)  # Width of the lines
            # To start creating lines (you also have glBegin(GL_TRIANGLES), glBegin(GL_POLYGONES), etc....
            # depending on what you want to draw)
            glBegin(GL_LINES)
            # X axis (red)
            glColor3ub(255, 0, 0)
            glVertex3d(0, 0, 0)  # The first glVertex3d is the starting point and the second the end point
            glVertex3d(1, 0, 0)
            # Y axis (green)
            glColor3ub(0, 255, 0)
            glVertex3d(0, 0, 0)
            glVertex3d(0, 1, 0)
            # Z axis (blue)
            glColor3ub(0, 0, 255)
            glVertex3d(0, 0, 0)
            glVertex3d(0, 0, 1)
            glEnd()  # Stop
            glLineWidth(1.0)  # Change back the width to default if you want to draw something else after normally

        else:
            if PCA_done == False:
                # display input 3D model
                if InputModelLoaded == True and InputTextureLoaded == True:
                    self.updated.emit(1)
                    glClearColor(bg_color, bg_color, bg_color, 1.0)
                    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                    glMatrixMode(GL_PROJECTION)
                    glLoadIdentity()  # identity matrix, resets the matrix back to its default state
                    # field of view (angle), ratio, near plane, far plane, all values must be > 0
                    gluPerspective(60, 1, 0.01, 10000)
                    glMatrixMode(GL_MODELVIEW)
                    glLoadIdentity()
                    glTranslate(Tx, Ty, -Tz)
                    glRotated(self.xRot / 16, 1.0, 0.0, 0.0)
                    glRotated(self.yRot / 16, 0.0, 1.0, 0.0)
                    glRotated(self.zRot / 16, 0.0, 0.0, 1.0)
                    # Move 3D object to center
                    glPushMatrix()  # Save any translate/scale/rotate operations that you previously used
                    # In InputModel.vertices you have the coordinates of the vertices (X,Y,Z)
                    InputModel_Xs = [row[0] for row in InputModel.vertices]  # Here you will extract X
                    InputModel_Ys = [row[1] for row in InputModel.vertices]  # Here you will extract Y
                    InputModel_Zs = [row[2] for row in InputModel.vertices]  # Here you will extract Z
                    # A 3D object can have coordinates not always centered on 0
                    # So we are calculating u0,v0,w0 (center of mass/gravity of the 3D model)
                    # To be able to move it after to the center of the scene
                    u0 = (min(InputModel_Xs) + max(InputModel_Xs)) / 2
                    v0 = (min(InputModel_Ys) + max(InputModel_Ys)) / 2
                    w0 = (min(InputModel_Zs) + max(InputModel_Zs)) / 2
                    # Here we are calculating the best zoom factor by default (to see the 3D model entirely)
                    d1 = max(InputModel_Xs) - min(InputModel_Xs)
                    d2 = max(InputModel_Ys) - min(InputModel_Ys)
                    d3 = max(InputModel_Zs) - min(InputModel_Zs)
                    Q = 0.5 / ((d1 + d2 + d3) / 3)
                    glScale(Q, Q, Q)
                    glTranslate(-u0, -v0, -w0)  # Move the 3D object to the center of the scene
                    # Display 3D Model via a CallList (GOOD, extremely fast!)
                    # If the list is not created, we will do it
                    if InputModelLoaded == True and InputTextureLoaded == True and InputListCreated == False:
                        ## This is how to set up a display list, whose invocation by glCallList
                        self.glinputModel = glGenLists(1)  # Allocate one list into memory
                        glNewList(self.glinputModel, GL_COMPILE)  # Begin building the passed in list
                        self.addTexture(InputTexturePath)  # Call function to add texture
                        self.addModel(InputModel)  # Call function to add 3D model
                        glEndList()  # Stop list creation
                        InputListCreated = True
                        c_mode = r_mode
                        glCallList(self.glinputModel)  # Call the list (display the model)
                    # If the list is already created, no need to process again and loose time, just display it
                    elif InputModelLoaded == True and InputTextureLoaded == True and InputListCreated == True:
                        # however, if we are changing the mode (Faces/Points), we need to recreate again
                        if Updated == True:
                            # Here we have to create the list again because it's not exactly the same list
                            # if we want to show just the points or the full model
                            self.glinputModel = glGenLists(1)
                            glNewList(self.glinputModel, GL_COMPILE)
                            self.addTexture(InputTexturePath)
                            self.addModel(InputModel)
                            glEndList()
                            c_mode = r_mode
                            glCallList(self.glinputModel)
                            Updated = False
                        else:
                            glCallList(self.glinputModel)
                    glPopMatrix()  # Will reload the old model view matrix
                else:
                    print(0)

            # if the PCA is done, we will display the new model here
            else:
                glClearColor(bg_color, bg_color, bg_color, 1.0)
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                glMatrixMode(GL_PROJECTION)
                glLoadIdentity()  # identity matrix, resets the matrix back to its default state
                gluPerspective(60, 1, 0.01, 10000)
                glMatrixMode(GL_MODELVIEW)
                glLoadIdentity()
                glTranslate(Tx, Ty, -Tz)
                glRotated(self.xRot / 16, 1.0, 0.0, 0.0)
                glRotated(self.yRot / 16, 0.0, 1.0, 0.0)
                glRotated(self.zRot / 16, 0.0, 0.0, 1.0)
                # Move 3D object to center
                glPushMatrix()  # Save any translate/scale/rotate operations that you previously used
                # In InputModel.vertices you have the coordinates of the vertices (X,Y,Z), here you will extract X
                InputModel_Xs = [row[0] for row in InputModel.vertices]
                InputModel_Ys = [row[1] for row in InputModel.vertices]  # Here you will extract Y
                InputModel_Zs = [row[2] for row in InputModel.vertices]  # Here you will extract Z
                u0 = (min(InputModel_Xs) + max(InputModel_Xs)) / 2
                v0 = (min(InputModel_Ys) + max(InputModel_Ys)) / 2
                w0 = (min(InputModel_Zs) + max(InputModel_Zs)) / 2
                # Here we are calculating the best zoom factor by default (to see the 3D model entirely)
                d1 = max(InputModel_Xs) - min(InputModel_Xs)
                d2 = max(InputModel_Ys) - min(InputModel_Ys)
                d3 = max(InputModel_Zs) - min(InputModel_Zs)
                Q = 0.5 / ((d1 + d2 + d3) / 3)
                glScale(Q, Q, Q)
                glTranslate(-u0, -v0, -w0)  # Move the 3D object to the center of the scene
                self.setXRotation(LeftXRot)
                self.setYRotation(LeftYRot)
                self.updated.emit(1)
                if TargetListCreated == False:
                    ##This is how to set up a display list, whose invocation by glCallList
                    self.targetModel = glGenLists(1)
                    glNewList(self.targetModel, GL_COMPILE)
                    self.applyTarTexture(TarTexture)
                    self.addModel(InputModel)
                    glEndList()
                    TargetListCreated = True
                    c_mode = r_mode
                    glCallList(self.targetModel)
                elif TargetListCreated == True:
                    if c_mode == r_mode and old_Gval == Gval and old_Tval == Tval:
                        glCallList(self.targetModel)
                    else:
                        self.targetModel = glGenLists(1)
                        glNewList(self.targetModel, GL_COMPILE)
                        self.applyTarTexture(TarTexture)
                        self.addModel(InputModel)
                        glEndList()
                        c_mode = r_mode
                        glCallList(self.targetModel)
                old_Gval = Gval
                old_Tval = Tval
                glPopMatrix()

    def addModel(self, InputModel):
        if r_mode == "Faces":
            glEnable(GL_TEXTURE_2D)
            glEnable(GL_DEPTH_TEST)  # to show all faces
            # glEnable(GL_CULL_FACE) # To hide non visible faces
            glBindTexture(GL_TEXTURE_2D, self.tex)
            glBegin(GL_TRIANGLES)
            for i in InputModel.faces:
                F = i[0]
                for j in F:
                    glColor3ub(255, 255, 255)
                    glTexCoord2f(InputModel.texcoords[j-1][0], InputModel.texcoords[j-1][1])
                    glNormal3d(InputModel.normals[j-1][0], InputModel.normals[j-1][1], InputModel.normals[j-1][2])
                    glVertex3d(InputModel.vertices[j-1][0], InputModel.vertices[j-1][1], InputModel.vertices[j-1][2])
            glEnd()
            glDisable(GL_TEXTURE_2D)
        elif r_mode == "Points":
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.tex)
            glBegin(GL_POINTS)
            for i in range(len(InputModel.vertices)):
                glColor3ub(255, 255, 255)
                glTexCoord2f(InputModel.texcoords[i][0], InputModel.texcoords[i][1])
                glNormal3d(InputModel.normals[i][0], InputModel.normals[i][1], InputModel.normals[i][2])
                glVertex3d(int(InputModel.vertices[i][0]), int(InputModel.vertices[i][1]), int(InputModel.vertices[i][2]))
            glEnd()
            glDisable(GL_TEXTURE_2D)

    def addTexture(self, TexturePath):
        img = QtGui.QImage(TexturePath)
        img = QGLWidget.convertToGLFormat(img)
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width(), img.height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, img.bits().asstring(img.byteCount()))





    def applyTarTexture(self, TarTexture):
        img = QtGui.QImage("TarTexture.png")
        img = QGLWidget.convertToGLFormat(img)
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width(), img.height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, img.bits().asstring(img.byteCount()))

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def wheelEvent(self, event):
        global Tz
        numDegrees = event.angleDelta() / 8
        orientation = numDegrees.y()
        if orientation > 0:
            Tz -= 0.1  # zoom out
        else:
            Tz += 0.1  # zoom in
        self.updateGL()

    def mouseMoveEvent(self, event):
        global Tx, Ty, Tz
        global LeftXRot, LeftYRot
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()
        if event.buttons() & Qt.LeftButton:  # holding left button of mouse and moving will rotate the object
            self.setXRotation(self.xRot + 8 * dy)
            self.setYRotation(self.yRot + 8 * dx)
            LeftXRot = self.xRot + 8 * dy
            LeftYRot = self.yRot + 8 * dx
        elif event.buttons() & Qt.RightButton:  # holding right button of mouse and moving will translate the object
            Tx += dx / 100
            Ty -= dy / 100
            self.updateGL()
        elif event.buttons() & Qt.MidButton:  # holding middle button of mouse and moving will reset zoom/translations
            Tx = Ty = 0
            Tz = 1
            self.setXRotation(0)
            self.setYRotation(90)
            self.updateGL()

        self.lastPos = event.pos()

    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 50:
            return

        glViewport(round((width - side) / 2), round((height - side) / 2), side, side)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, 1, 0.01, 10000)
        glMatrixMode(GL_MODELVIEW)

    def setClearColor(self, c):
        gl.glClearColor(c.redF(), c.greenF(), c.blueF(), c.alphaF())

    def setColor(self, c):
        gl.glColor4f(c.redF(), c.greenF(), c.blueF(), c.alphaF())

    def setXRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.xRot:
            self.xRot = angle
            self.xRotationChanged.emit(angle)
            self.update()

    def setYRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.xRot:
            self.yRot = angle
            self.yRotationChanged.emit(angle)
            self.update()

    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.xRot:
            self.zRot = angle
            self.zRotationChanged.emit(angle)
            self.update()

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle



###########################################
# BONUS TASKS
###########################################
#
# Implement the PCA on the whole database and link some of the principles components to more sliders
# so you can create something even more unique
# You may need to use threads because of the processing time
# Adapt the 2 classes below and move the PCA in them

####################################################################################################
# The Geometry Thread
####################################################################################################
class GeometryThreadClass(QThread):
    updated = pyqtSignal(int)
    running = False

    def __init__(self, parent=None):
        super(GeometryThreadClass, self).__init__(parent)
        self.running = True

    def run(self):
        if self.running == True:
            self.PCAGeometry()

    def stop(self):
        self.running = False

    def PCAGeometry(self):
        global Root, b_ProcessDone
        global OriModel, TarModel
        global ITval, SFval, b_Ready

        ### MOVE PCA HERE
        OriModel = OBJFastV("model1.obj")
        TarModel = OBJFastV("model2.obj")

        versize = len(OriModel.vertices)

        numImages = 2
        data = np.zeros((numImages, versize * 3),dtype=np.float32)

        vertices = np.asarray(OriModel.vertices)

        count = 0
        for x in range(5904):
            data[0][count] = vertices[x][0]
            x += 1
            count += 1
        
        for y in range(5904):
            data[0][count] = vertices[y][1]
            y += 1
            count += 1
        
        for z in range(5904):
            data[0][count] = vertices[z][2]
            z += 1
            count += 1


        vertices = np.asarray(TarModel.vertices)

        count = 0
        for x in range(5904):
            data[1][count] = vertices[x][0]
            x += 1
            count += 1
        
        for y in range(5904):
            data[1][count] = vertices[y][1]
            y += 1
            count += 1
        
        for z in range(5904):
            data[1][count] = vertices[z][2]
            z += 1
            count += 1

        mu = np.mean(data, 0)
        ma_data = data - mu
        e_faces, sigma, v = linalg.svd(ma_data.transpose(), full_matrices=False)
        weights = np.dot(ma_data, e_faces)

        ## Once the PCA is done, save the results (to be able to use them with the sliders)
        ## The global variable Root['models'] is related to the geometry
        Root['models'] = {}
        ## Save results
        Root['models']['VrGeo'] = e_faces.T  # eigenvector variable
        Root['models']['XmGeo'] = mu # average geometry variable
        Root['models']['WGeo'] = [weights[0, 0], weights[1, 0]] # min and max weights : [min, max]

        b_ProcessDone = True


####################################################################################################
# The Texture Thread
####################################################################################################
class TextureThreadClass(QThread):
    updated = pyqtSignal(int)
    running = False

    def __init__(self, parent=None):
        super(TextureThreadClass, self).__init__(parent)
        self.running = True

    def run(self):
        if self.running == True:
            self.PCATexture()

    def stop(self):
        self.running = False

    def PCATexture(self):
        global Root, b_Process2Done
        global OriModel, OriTexturePath
        global TarModel, TarTexturePath
        global ITval, SFval

        ### MOVE PCA HERE

        texA = imread("model1.png")
        texB = imread("model2.png")

        textures = [texA, texB]
        images = [  np.float32(i/255) for i in textures ]

        numImages = 2
        texsize = texA.shape

        data = np.zeros((numImages, texsize[0]*texsize[1]*texsize[2]),dtype=np.float32)
        for i in range(0, numImages):
            image = images[i].flatten(order='K')
            data[i,:] = image

        mu = np.mean(data, 0)
        ma_data = data - mu
        e_faces, sigma, v = linalg.svd(ma_data.transpose(), full_matrices=False)
        weights = np.dot(ma_data, e_faces)


        # Instead of saving in a yml file, we will save a structure
        # The global variable Root['Tex'] is related to the texture
        Root['Tex'] = {}
        ## Save results
        Root['Tex']['VrTex'] = e_faces.T  # eigenvector variable (transpose)
        Root['Tex']['XmTex'] = mu  # average texture variable
        Root['Tex']['WTex'] = [weights[0, 0], weights[1, 0]]  # min and max weights : [min, max]


        b_Process2Done = True



if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())
