#!/usr/bin/env pythonw
 
import sys
import vtk
import textured_objects as tobs
import animations

from gui              import *
from nc_file_readers  import *
from PyQt4            import QtCore, QtGui
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

def select_scalar_field(i):
  print("select index ",i)

#_______________________________________________________________________
def open_a_file():

  global window, ren

  print("open a file")
  window.statusBar().showMessage('Open Local File')

  # get filename and show only files matching *
  filename = QtGui.QFileDialog.getOpenFileName(window, 'Open File',".","(*)")
  window.statusBar().showMessage('filename=' +filename)
  print("filename = ",filename)

  # allow qt to close the window and cleanup
  QtGui.QApplication.processEvents()


  # read netcdf header and create corresponding toolbars
  dataset        = read_netcdf_header(filename)

  fields_toolbar = NCToolbar  (window,dataset)
  time_toolbar   = TimeToolbar(window,dataset)

  fields_toolbar.scalars_combo.currentIndexChanged.connect(select_scalar_field)

  # create a lat-lon surface for interpolated data
  lons    = dataset.variables['lon']
  lats    = dataset.variables['lat']
  ps_var  = dataset.variables['ps' ]

  ps = ps_var[2,:,:]-ps_var[1,:,:]
  surfaceActor = make_latlon_surface(lats,lons,ps)

  # reset the scene to a blank slate
  ren.RemoveAllViewProps();
  ren.RemoveAllLights()

  ren.AddActor(surfaceActor)

  ren.ResetCamera()
  ren.GetActiveCamera().Zoom(1.2)
  ren.AutomaticLightCreationOn()
  ren.TwoSidedLightingOn()


#_______________________________________________________________________
def create_default_scene():
  global ren, iren

  # create textured sphere to represent the Earth
  earthSphere = tobs.TexturedSphere(0.99,"../images/earth.jpg")
  ren.AddActor(earthSphere.actor)

  # create spinning earth animation
  animation = animations.RevolveZAnimation(earthSphere.actor)
  iren.AddObserver('TimerEvent', animation.execute)

def loadFile(fileame):
  print("load file ",filename)

#_______________________________________________________________________
if __name__ == "__main__":

  app     = QtGui.QApplication(sys.argv)
  window  = MainWindow()
  ren     = window.renderer
  iren    = window.interactor

  window.openAction.triggered.connect(open_a_file)

  # create something interesting to look at, at startup
  create_default_scene()

  # set camera position, and lighting attributes
  ren.ResetCamera()
  ren.GetActiveCamera().Zoom(1.5)
  ren.SetLightFollowCamera(0)
  ren.TwoSidedLightingOn()

  # start tracking user input from vtk widget in window
  iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
  iren.Initialize()

  # create a repeating timer for animations
  timerID = iren.CreateRepeatingTimer(20)

  sys.exit(app.exec_())

