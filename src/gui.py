#!/usr/bin/env pythonw
 
import sys
import vtk
from PyQt4 import QtCore, QtGui
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

import textured_objects as tobs
import animations

class MainWindow(QtGui.QMainWindow):

  #_____________________________________________________________________
  def __init__(self, parent = None):

    QtGui.QMainWindow.__init__(self, parent)

    # set the window size and title
    screen = QtGui.QApplication.desktop().screenGeometry()
    height = screen.height();
    width  = screen.width();
    self.setGeometry(width*0.1, height*0.1, width*0.8, height*0.8)
    self.setWindowTitle('viztool')

    # add a status bar at the bottom
    self.statusBar()

    # add QVTKRenderWindowInteractor to window
    self.frame      = QtGui.QFrame()
    self.vl         = QtGui.QVBoxLayout()
    self.vtkWidget  = QVTKRenderWindowInteractor(self.frame)
    self.vl.addWidget(self.vtkWidget)
    self.renderer        = vtk.vtkRenderer()
    self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
    self.interactor = self.vtkWidget.GetRenderWindow().GetInteractor()
    self.frame.setLayout(self.vl)
    self.setCentralWidget(self.frame)

    # add the menubar and file menus
    self.init_menubar()

    # add a toolbar
    self.toolbar = self.addToolBar("toolbar")

    # show window and begin tracking input from vtk widget
    self.show()

    self.statusBar().showMessage('Ready')

  #_____________________________________________________________________
  def init_menubar(self):

    # add a menubar attached to the top of the window
    menubar  = self.menuBar()
    menubar.setNativeMenuBar(False)

    # create a file menu
    fileMenu = menubar.addMenu('&File')

    # add open action to the file menu
    openAction = QtGui.QAction("&Open",self)
    openAction.setShortcut("Ctrl+O")
    openAction.triggered.connect(self.open)
    fileMenu.addAction(openAction)

    # add quit action to the file menu
    quitAction = QtGui.QAction(QtGui.QIcon('exit.png'),'&Quit',self)
    quitAction.setShortcut('Ctrl+Q')
    quitAction.setStatusTip('Exit Application')
    quitAction.triggered.connect(QtGui.qApp.quit)
    fileMenu.addAction(quitAction)

  #_____________________________________________________________________
  def open(self):

    # Get filename and show only files matching *
    self.statusBar().showMessage('Open Local File')
    self.filename = QtGui.QFileDialog.getOpenFileName(self, 'Open File',".","(*)")
    self.statusBar().showMessage('filename='+self.filename)
