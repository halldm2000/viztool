#!/usr/bin/env pythonw
 
import sys
import vtk
from PyQt4 import QtCore, QtGui
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

import textured_objects as tobs
import animations

class MainWindow(QtGui.QMainWindow):
 
  def __init__(self, parent = None):

    QtGui.QMainWindow.__init__(self, parent)

    exitAction = QtGui.QAction(QtGui.QIcon('exit.png'),'&Quit',self)
    exitAction.setShortcut('Ctrl+Q')
    exitAction.setStatusTip('Exit Application')
    exitAction.triggered.connect(QtGui.qApp.quit)

    openAction = QtGui.QAction("&Open",self)
    openAction.setShortcut("Ctrl+O")
    openAction.triggered.connect(self.open)

    self.statusBar()

    rec = QtGui.QApplication.desktop().screenGeometry()
    height = rec.height();
    width  = rec.width();
    self.setGeometry(width*0.1,height*0.1,width*0.8,height*0.8)
    self.setWindowTitle('viztool')

    self.frame      = QtGui.QFrame()
    self.vl         = QtGui.QVBoxLayout()
    self.vtkWidget  = QVTKRenderWindowInteractor(self.frame)
    self.vl.addWidget(self.vtkWidget)
    self.ren        = vtk.vtkRenderer()
    self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
    self.iren       = self.vtkWidget.GetRenderWindow().GetInteractor()

    # create textured sphere to represent the Earth
    earthSphere = tobs.TexturedSphere(0.99,"../images/earth.jpg")
    self.ren.AddActor(earthSphere.actor)

    self.ren.ResetCamera()
    self.ren.GetActiveCamera().Zoom(1.5)
    self.ren.SetLightFollowCamera(0)
    self.ren.TwoSidedLightingOn()

    self.frame.setLayout(self.vl)
    self.setCentralWidget(self.frame)

    menubar  = self.menuBar()
    menubar.setNativeMenuBar(False)
    fileMenu = menubar.addMenu('&File')
    fileMenu.addAction(openAction)
    fileMenu.addAction(exitAction)

    self.toolbar = self.addToolBar("toolbar")

    self.show()
    self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    self.iren.Initialize()

    self.statusBar().showMessage('Ready')
    animation = animations.RevolveZAnimation(earthSphere.actor)
    self.iren.AddObserver('TimerEvent', animation.execute)

    # create a repeating timer event
    timerID = self.iren.CreateRepeatingTimer(20)

  def open(self):
    # Get filename and show only .writer files
    self.statusBar().showMessage('Open Local File')
    self.filename = QtGui.QFileDialog.getOpenFileName(self, 'Open File',".","(*)")
    self.statusBar().showMessage('filename='+self.filename)

if __name__ == "__main__":
 
    app     = QtGui.QApplication(sys.argv)
    window  = MainWindow()
    sys.exit(app.exec_())

