from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QSlider, QGridLayout, QLabel, QPushButton, QTextEdit, QComboBox, QCheckBox
import PyQt6.QtCore as QtCore
from PyQt6.QtCore import Qt
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import argparse
import sys
import json 
import numpy as np
import time
frame_counter = 0

def save_frame(window, log):
    global frame_counter
    global args
    # ---------------------------------------------------------------
    # Save current contents of render window to PNG file
    # ---------------------------------------------------------------
    file_name = args.output + str(frame_counter).zfill(5) + ".png"
    image = vtk.vtkWindowToImageFilter()
    image.SetInput(window)
    png_writer = vtk.vtkPNGWriter()
    png_writer.SetInputConnection(image.GetOutputPort())
    png_writer.SetFileName(file_name)
    window.Render()
    png_writer.Write()
    frame_counter += 1
    if args.verbose:
        print(file_name + " has been successfully exported")
    log.insertPlainText('Exported {}\n'.format(file_name))

def print_data(data, text_window, log):
    #Print stats mean, min, max, std
    text_window.setHtml("<div style='font-weight: bold'>Data Statistics</div>")
    text_window.append("Min: {}".format(data['min']))
    text_window.append("Max: {}".format(data['max']))
    text_window.append("Mean: {}".format(data['mean']))
    text_window.append("Std: {}".format(data['std']))
    text_window.append("Co-Var: {}".format(data['cv']))
    log.insertPlainText('Retrieved data\n');


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName('The Main Window')
        MainWindow.setWindowTitle('MW-M31-VTK')
        self.centralWidget = QWidget(MainWindow)
        self.gridlayout = QGridLayout(self.centralWidget)
        self.vtkWidget = QVTKRenderWindowInteractor(self.centralWidget)
        # Sliders
        self.slider_magnitude = QSlider()
        self.mag_label = QLabel()
        self.mag_label.setText('Density Threshold')
        self.slider_label = QLabel()
        self.slider_scale = QSlider()
        self.scale_label = QLabel()
        self.scale_label = QLabel('Scale')
        self.scale_value = QLabel(str(1))
        # Push buttons
        self.push_data = QPushButton()
        self.push_data.setText('Update data')
        self.push_quit = QPushButton()
        self.push_quit.setText('Quit')
        self.reset_camera = QPushButton()
        self.reset_camera.setText('Reset Camera')
        self.dropdown = QComboBox()
        self.checkbox = QCheckBox()
        self.checkbox.setText('Arrow Source')
        self.dropdown.addItems(['Density', 'Internal Energy', 'Velocity', 'Magnetic Field'])
        self.data_text = QTextEdit()
        self.data_text.setReadOnly(True)
        self.data_text.setAcceptRichText(True)
        self.data_text.setHtml("<div style='font-weight: bold'>Data Statistics</div>")
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.gridlayout.addWidget(self.vtkWidget, 0, 0, 4, 4)
        self.gridlayout.addWidget(self.mag_label, 4, 0, 1, 1)
        self.gridlayout.addWidget(self.slider_label, 4, 2, 1, 1)
        self.gridlayout.addWidget(self.slider_magnitude, 4, 1, 1, 1)
        self.gridlayout.addWidget(self.scale_label, 5, 0, 1, 1)
        self.gridlayout.addWidget(self.scale_value, 5, 2, 1, 1)
        self.gridlayout.addWidget(self.slider_scale, 5, 1, 1, 1)
        self.gridlayout.addWidget(self.reset_camera, 0, 5, 1, 1)
        self.gridlayout.addWidget(self.checkbox, 1, 4, 1, 1)
        self.gridlayout.addWidget(self.push_data, 1, 5, 1, 1)
        self.gridlayout.addWidget(self.dropdown, 0, 4, 1, 1)
        self.gridlayout.addWidget(self.push_quit, 5, 5, 1, 1)
        self.gridlayout.addWidget(self.data_text, 2, 4, 1, 2)
        self.gridlayout.addWidget(self.log, 3, 4, 1, 2)
        self.gridlayout.addWidget(self.push_quit, 5, 5, 1, 1)
        MainWindow.setCentralWidget(self.centralWidget)

class Galaxy(QMainWindow):

    def make_ctfs(self):
        attr = 0         
        self.ctf_objects[attr] = vtk.vtkColorTransferFunction()
        with open(args.ctf, 'r') as f:
            for line in f:
                if(line == '#\n'):
                    attr += 1
                    self.ctf_objects[attr] = vtk.vtkColorTransferFunction()
                    if(attr == 2 or attr == 3):
                        self.ctf_objects[attr].SetVectorModeToMagnitude()
                    else:
                        self.ctf_objects[attr].SetVectorModeToComponent()
                else:
                    val, r, g, b = line.split(" ")
                    self.ctf_objects[attr].AddRGBPoint(float(val), float(r), float(g), float(b))
            
    def __init__(self, parent = None):
        QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.magntitude = 0
        self.scale = 10
        self.attribute = 0
        self.attribute2string = {0: 'Density', 1: 'Internal Energy', 2: 'Velocity', 3: 'Magnetic Field'}
        self.ctf_objects = {}
        self.arrows_enabled = False
        self.make_ctfs()
        # Source
        self.reader = vtk.vtkUnstructuredGridReader()
        self.reader.SetFileName(args.andro)
        self.reader.Update()

        #Sphere source
        self.sphere = vtk.vtkSphereSource()
        self.sphere.SetRadius(0.5)
        self.sphere.SetThetaResolution(10)
        self.sphere.SetPhiResolution(10)
        self.sphere.Update()

        #Threshold filter
        self.threshold = vtk.vtkThresholdPoints()
        self.threshold.SetInputConnection(self.reader.GetOutputPort())
        self.threshold.SetInputArrayToProcess(0, 0, 0, 0, self.attribute2string[self.attribute])
        
        #Glyph
        self.glyph = vtk.vtkGlyph3D()
        self.glyph.SetInputConnection(self.threshold.GetOutputPort())
        self.glyph.SetSourceConnection(self.sphere.GetOutputPort())
        self.glyph.SetScaleFactor(0.15)
        self.glyph.SetVectorModeToUseVector()
        self.glyph.Update()
        
        self.mapper = vtk.vtkDataSetMapper()
        self.mapper.SetInputConnection(self.glyph.GetOutputPort())
        self.mapper.SetLookupTable(self.ctf_objects[self.attribute])
        self.mapper.SelectColorArray(self.attribute2string[self.attribute])
        #color by magnitude of vector
        self.mapper.SetScalarModeToUsePointFieldData()
        self.mapper.Update()

        #Scalar bar 
        self.scalar_bar = vtk.vtkScalarBarActor()
        self.scalar_bar.SetLookupTable(self.mapper.GetLookupTable())
        self.scalar_bar.SetTitle(self.attribute2string[self.attribute])
        self.scalar_bar.SetNumberOfLabels(5)
        
        self.scalar_bar.SetPosition(0.85, 0.1)
        self.scalar_bar.SetWidth(0.1)
        self.scalar_bar.SetHeight(0.7)
        self.scalar_bar.SetPosition(0.85, 0.15)
        self.scalar_bar.SetOrientationToVertical()
        
        self.dropdown_callback(0) #init to density attribute
        actor = vtk.vtkActor()
        actor.SetMapper(self.mapper)
        # Add lighting
        light = vtk.vtkLight()
        light.SetPosition(1, 1, 1)
        
        # Create the Renderer
        self.ren = vtk.vtkRenderer()
        self.ren.AddActor(actor)
        self.ren.AddLight(light)
        self.ren.AddActor(self.scalar_bar)
        self.ren.GradientBackgroundOn()  
        self.ren.SetBackground(0,0,0)  
        self.ui.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.ui.vtkWidget.GetRenderWindow().GetInteractor()

        camera = self.ren.GetActiveCamera()
        camera.SetPosition(25079.40097592641, 5916.434613488837, 34220.7539577094)
        camera.SetFocalPoint(25043.3505859375, 5825.639892578125, 34192.19921875)
        camera.SetViewUp(-0.20501092159116302, 0.3667866353001687, -0.9074348936389448)
        camera.SetClippingRange(31.128360222187, 190.95598868960982)
        
        # Setting up widgets
        def slider_setup( slider, val):
            #int((self.max_value - self.min_value) / self.interval))

            slider.setOrientation(Qt.Orientation.Horizontal)
            slider.setValue(int(val))
            slider.setTracking(False)
            slider.setTickInterval(1)
            slider.setTickPosition(QSlider.TickPosition.TicksAbove)
            slider.setRange(0, 10)
            
       
        range_ = self.ctf_objects[self.attribute].GetRange()
        slider_setup(self.ui.slider_magnitude, self.magntitude)
        slider_setup(self.ui.slider_scale, self.scale)

    def mag_callback(self, val):
        min, max = self.ctf_objects[self.attribute].GetRange()
        self.magntitude = val 
        interval = (max-min)/10
        val = min + interval * (val)

        self.ui.slider_label.setText(str(val))
        self.ui.log.insertPlainText('Magnitude set to {}\n'.format(val))
        #update threshold
        self.threshold.SetUpperThreshold(val)
        self.ui.vtkWidget.GetRenderWindow().Render()

    def scale_callback(self, val):
        self.ui.scale_value.setText(str(val))
        if(self.arrows_enabled):
            val = val * 0.05
        else:    
            val = val * 0.15
        self.scale = val
        self.ui.log.insertPlainText('Scale set to {}\n'.format(self.scale))
        #update glyph scale
        self.glyph.SetScaleFactor((self.scale)/10)
        self.ui.vtkWidget.GetRenderWindow().Render()
        
    def screenshot_callback(self):
        save_frame(self.ui.vtkWidget.GetRenderWindow(), self.ui.log)
    
    def checkbox_callback(self):
        if self.ui.checkbox.isChecked():
            arrow_glyph = vtk.vtkGlyph3D()
            arrow = vtk.vtkArrowSource()
            arrow_glyph.SetInputConnection(self.reader.GetOutputPort())
            arrow_glyph.SetSourceConnection(arrow.GetOutputPort())
            if(self.attribute == 2):
                arrow_glyph.SetScaleFactor(0.0025)
            elif(self.attribute == 3):
                arrow_glyph.SetScaleFactor(0.1)
            arrow_glyph.SetInputArrayToProcess(0, 0, 0, 0, self.attribute2string[self.attribute].replace(' ', ''))
            #color by magnitude
            arrow_glyph.Update()
            arrow_mapper = vtk.vtkDataSetMapper()
            arrow_mapper.SetInputConnection(arrow_glyph.GetOutputPort())
            arrow_mapper.Update()
            self.arrow_actor = vtk.vtkActor()
            self.arrow_actor.SetMapper(arrow_mapper)
            self.ren.AddActor(self.arrow_actor)
        else:
            if(self.arrow_actor):
                self.ren.RemoveActor(self.arrow_actor)
                self.arrow_actor = None 
            self.arrows_enabled = False
            self.glyph.SetSourceConnection(self.sphere.GetOutputPort())
            self.glyph.SetScaleFactor(self.scale*(0.15)/10)
            self.glyph.Update()
        self.ui.vtkWidget.GetRenderWindow().Render()
    def get_stats(self, mag_data):
        stats = {}
        stats['min'] = np.min(mag_data)
        stats['max'] = np.max(mag_data)
        stats['mean'] = np.mean(mag_data)
        stats['std'] = np.std(mag_data)
        stats['cv'] = stats['std']/stats['mean']*100
        return stats
    
    def data_callback(self):
        mag_data = self.reader.GetOutput().GetPointData().GetArray(self.attribute2string[self.attribute].replace(' ', ''))
        if(self.attribute == 2 or self.attribute == 3):
            #only use magnitude of velocity and magnetic field
            mag_data = np.linalg.norm(mag_data, axis=1)
        stats = self.get_stats(mag_data)
        print_data(stats, self.ui.data_text, self.ui.log)

    def dropdown_callback(self, val):
        self.attribute = val
        min, max = self.ctf_objects[self.attribute].GetRange()
        attribute_str = self.attribute2string[self.attribute]
        #Update slider text
        self.ui.mag_label.setText(str(attribute_str + ' Threshold'))
        
        self.ui.checkbox.setChecked(False)
        #Update checkbox 
        if(self.attribute == 2 or self.attribute == 3):
            self.ui.checkbox.setEnabled(True)
        else:
            self.ui.checkbox.setEnabled(False)
        #data range from array
        self.mapper.SetLookupTable(self.ctf_objects[self.attribute])
        self.mapper.SelectColorArray(attribute_str.replace(' ', ''))
        #update scalar bar
        self.scalar_bar.SetLookupTable(self.mapper.GetLookupTable())
        self.scalar_bar.SetTitle(attribute_str)

        self.threshold.SetInputArrayToProcess(0, 0, 0, 0, self.attribute2string[self.attribute].replace(' ', ''))
        if(self.attribute == 2 or self.attribute == 3):
            self.threshold.SetInputArrayComponent(4)
        self.threshold.SetUpperThreshold(self.ctf_objects[self.attribute].GetRange()[0])
        
        
        self.magntitude = 0
        self.ui.slider_magnitude.setValue(0)
        label = min + (max-min)/10 * (self.magntitude)
        self.ui.slider_label.setText(str(label))
    
        self.ui.vtkWidget.GetRenderWindow().Render()
        
    def reset_camera(self):
        camera = self.ren.GetActiveCamera()
        camera.SetPosition(25079.40097592641, 5916.434613488837, 34220.7539577094)
        camera.SetFocalPoint(25043.3505859375, 5825.639892578125, 34192.19921875)
        camera.SetViewUp(-0.20501092159116302, 0.3667866353001687, -0.9074348936389448)
        camera.SetClippingRange(31.128360222187, 190.95598868960982)
        self.ui.vtkWidget.GetRenderWindow().Render()
        
    def quit_callback(self):
        sys.exit()

if __name__=="__main__":
    global args

    parser = argparse.ArgumentParser(
        description='Visualize the IllustrisTNG galaxy')
    parser.add_argument("-a", "--andro", help="andromeda .vtk file", required=True)
    parser.add_argument("-c", "--ctf", help="CTF .txt file", required=True)

    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = Galaxy()
    #full screen resolution
    render_window = window.ui.vtkWidget.GetRenderWindow()
    render_window.SetSize(render_window.GetScreenSize())
    window.show()
    window.setWindowState(Qt.WindowState.WindowMaximized)  # Maximize the window
    window.iren.Initialize() # Need this line to actually show
                             # the render inside Qt

    window.ui.slider_magnitude.valueChanged.connect(window.mag_callback)
    window.ui.slider_scale.valueChanged.connect(window.scale_callback)
    window.ui.push_data.clicked.connect(window.data_callback)
    window.ui.dropdown.currentIndexChanged.connect(window.dropdown_callback)
    window.ui.checkbox.stateChanged.connect(window.checkbox_callback)
    window.ui.push_quit.clicked.connect(window.quit_callback)
    window.ui.reset_camera.clicked.connect(window.reset_camera)
    sys.exit(app.exec())
