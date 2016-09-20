#!/usr/bin/env pythonw
 
import sys
import vtk
from PyQt4 import QtCore, QtGui

from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from netCDF4 import Dataset

import textured_objects as tobs
import animations

#_______________________________________________________________________
class MainWindow(QtGui.QMainWindow):

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
    self.vl.setContentsMargins(5,5,5,5)
    self.vtkWidget  = QVTKRenderWindowInteractor(self.frame)
    self.vl.addWidget(self.vtkWidget)
    self.renderer   = vtk.vtkRenderer()
    self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
    self.interactor = self.vtkWidget.GetRenderWindow().GetInteractor()
    self.frame.setLayout(self.vl)
    self.setCentralWidget(self.frame)

    # add the menubar and file menus
    self.init_menubar()

    # add a toolbar
    self.toolbar = self.addToolBar("toolbar")
    self.toolbar.setMovable(False)
    #iconSize = QtCore.QSize(24, 24)
    #self.toolbar.setIconSize(iconSize)

    # add a combo box in the toolbar
    #self.combo = QtGui.QComboBox()
    #self.toolbar.addWidget(self.combo)
    #self.combo.insertItems(1,["One","Two","Three"])


    # add another toolbar
    #self.toolbar2 = self.addToolBar("toolbar2")
    #self.toolbar2.addAction('action!')

    # show window and begin tracking input from vtk widget
    self.show()
    self.statusBar().showMessage('Ready')

  #.....................................................................
  def init_menubar(self):

    # add a menubar attached to the top of the window
    menubar  = self.menuBar()
    menubar.setNativeMenuBar(False)

    # create a file menu
    fileMenu = menubar.addMenu('&File')

    # add open action to the file menu
    self.openAction = QtGui.QAction("&Open",self)
    self.openAction.setShortcut("Ctrl+O")
    #openAction.triggered.connect(self.open)
    fileMenu.addAction(self.openAction)

    # add quit action to the file menu
    quitAction = QtGui.QAction(QtGui.QIcon('exit.png'),'&Quit',self)
    quitAction.setShortcut('Ctrl+Q')
    quitAction.setStatusTip('Exit Application')
    quitAction.triggered.connect(QtGui.qApp.quit)
    fileMenu.addAction(quitAction)

#_______________________________________________________________________
class TimeToolbar(QtGui.QToolBar):

  def __init__(self,window,dataset):

    super(TimeToolbar, self).__init__(window)
    window.addToolBar(self)

    self.setIconSize(QtCore.QSize(24, 24))
    self.setStyleSheet('QToolBar{spacing:10px;}')

    #self.addSeparator()
    self.addWidget(QtGui.QLabel("time index:"))
    self.time_index = QtGui.QLabel("0")
    self.addWidget(self.time_index)
    #self.addSeparator()

    # add a button for playing backward
    self.backwardButton = QtGui.QToolButton()
    self.backwardButton.setIcon(self.style().standardIcon(QtGui.QStyle.SP_MediaSeekBackward))
    self.backwardButton.setToolTip("Play Backward")

    # add a button for pausing time loop
    self.stopButton = QtGui.QToolButton()
    self.stopButton.setIcon(self.style().standardIcon(QtGui.QStyle.SP_MediaStop))
    self.stopButton.setToolTip("Stop")
    #self.stopButton.clicked.connect(self.movie.setPaused)

    # add a button for playing forward
    self.forwardButton = QtGui.QToolButton()
    self.forwardButton.setIcon(self.style().standardIcon(QtGui.QStyle.SP_MediaSeekForward))
    self.forwardButton.setToolTip("Play Forward")
    #self.playButton.clicked.connect(self.movie.start)

    self.addWidget(self.backwardButton)
    self.addWidget(self.stopButton)
    self.addWidget(self.forwardButton)

#_______________________________________________________________________
class NCToolbar(QtGui.QToolBar):

  def __init__(self,window,dataset):
    
    super(NCToolbar, self).__init__(window)

    self.setIconSize(QtCore.QSize(24, 24))
    self.setStyleSheet('QToolBar{spacing:10px;}')

    window.addToolBar(self)
    self.scalars_combo = QtGui.QComboBox()
    self.vectors_combo = QtGui.QComboBox()

    self.addWidget(QtGui.QLabel("scalar field:"))
    self.addWidget(self.scalars_combo)
    self.addWidget(QtGui.QLabel("vector field:"))
    self.addWidget(self.vectors_combo)

    # add scalar fields
    for variable in dataset.variables.values():
      ndim = variable.ndim
      dims = variable.dimensions
      print("var=",variable.name," dims=",dims)

      # add name to combobox if dimension > 1
      if(variable.ndim>1):
        dim_names = ','.join(dims)
        label = "{0} ({1})".format(variable.name,dim_names)
        self.scalars_combo.addItem(label)





