#!/usr/bin/env pythonw
 
import sys
import vtk
import textured_objects as tobs
import animations
import globals as g

from gui              import *
from nc_file_readers  import *
from PyQt4            import QtCore, QtGui
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

#_______________________________________________________________________
def set_time_index(i):
  g.time_index = i
  g.time_toolbar.time_index_label.setNum(i)
  select_scalar_field(g.sfield_index)

#_______________________________________________________________________
def increment_time_index():
  set_time_index(g.time_index+1)

#_______________________________________________________________________
def decrement_time_index():
  set_time_index(g.time_index-1)

#_______________________________________________________________________
def select_scalar_field(i):

  global window

  g.sfield_index = i
  text    = g.fields_toolbar.scalars_combo.itemText(i)
  varname = g.fields_toolbar.scalars_combo.itemData(i)

  if(i == 0):
    # no scalar field selected, hide data globe
    g.dataGlobe.VisibilityOff()
    g.scalarBar.VisibilityOff()

  else:
    # ensure data globe is visbile
    g.dataGlobe.VisibilityOn()
    g.scalarBar.VisibilityOn()

    field   = g.dataset.variables[varname]
    if(field.ndim ==4):
      field2d = field[g.time_index,g.level_index,:,:]
  
    if(field.ndim ==3):
      field2d = field[g.time_index,:,:]

    g.dataGlobe.set_scalar_field(field2d)

  window.renwin.Render()
  window.vtkWidget.setFocus()

#_______________________________________________________________________
def select_vector_field(i):
  pass

#_______________________________________________________________________
def select_map_projection(i):

  projection = g.projection_toolbar.projection_combo.itemData(i)
  print("projection=",projection)
  camera = ren.GetActiveCamera()

  if(projection=="globe"):

    g.map2dAssembly.VisibilityOff()
    g.globeAssembly.VisibilityOn()

    if(g.dataGlobe !=None):
      g.dataGlobe.VisibilityOn()

    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    ren.ResetCamera()
    camera.SetFocalPoint( 0.0, 0.0, 0.0 );
    camera.SetViewUp(0,1,0)
    camera.SetPosition(0,0,5)
    camera.SetClippingRange(0.1,20)

  elif(projection=="map2d"):

    g.globeAssembly.VisibilityOff()
    g.map2dAssembly.VisibilityOn()

#if(g.dataGlobe !=None):
#  g.dataGlobe.VisibilityOff()

#g.textureGlobe.VisibilityOff()

    g.mapActor.VisibilityOn()
    iren.SetInteractorStyle(vtk.vtkInteractorStyleImage())
    ren.ResetCamera()
    camera.SetFocalPoint( 0.0, 0.0, 0.0 );
    camera.SetViewUp(0,1,0)
    camera.SetPosition(0,0,2.5)
    camera.SetClippingRange(0.1,10)

  window.renwin.Render()
  window.vtkWidget.setFocus()

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
  g.dataset        = read_netcdf_header(filename)

  g.fields_toolbar = NCToolbar  (window,g.dataset)
  g.time_toolbar   = TimeToolbar(window)

  # hook up buttons and comboboxes
  g.fields_toolbar.scalars_combo.currentIndexChanged.connect(select_scalar_field)
  g.fields_toolbar.vectors_combo.currentIndexChanged.connect(select_vector_field)

  g.time_toolbar.nextButton.clicked.connect(increment_time_index)
  g.time_toolbar.previousButton.clicked.connect(decrement_time_index)

  # create a lat-lon surface for interpolated data
  lons    = g.dataset.variables['lon']
  lats    = g.dataset.variables['lat']

  # init color lookup table
  nc  = vtk.vtkNamedColors()
  g.lut = vtk.vtkLookupTable()
  g.lut.Build()
  g.lut.SetTableRange(0,1)
  g.lut.SetHueRange(0.0,1.0)
  g.lut.SetSaturationRange(1,1);
  g.lut.SetValueRange(1.0,1.0);

  # create a data sphere from nc data
  g.dataGlobe = tobs.QuadSphere(lats,lons)
  g.globeAssembly.AddPart(g.dataGlobe)

  # add scalar bar actor
  g.scalarBar = vtk.vtkScalarBarActor()
  g.scalarBar.SetOrientationToVertical()
  g.scalarBar.SetLookupTable(g.lut)
  g.scalarBar.SetWidth(0.08)
  g.scalarBar.SetPosition(0.90,0.1)
  g.scalarBar.SetTextPositionToPrecedeScalarBar()
  ren.AddActor(g.scalarBar)

  g.fields_toolbar.scalars_combo.setCurrentIndex(1)

#_______________________________________________________________________
def create_default_scene():
  global ren, iren

  # create textured sphere to represent the Earth
  g.textureGlobe = tobs.TexturedSphere(0.99,"../images/earth.jpg")
  g.globeAssembly = vtk.vtkAssembly()
  g.globeAssembly.AddPart(g.textureGlobe)
  ren.AddActor(g.globeAssembly)

  # create textured plane for 2d map

  g.map2dAssembly = vtk.vtkAssembly()
  g.map2dAssembly.VisibilityOff()
  ren.AddActor(g.map2dAssembly)

  g.mapActor = tobs.TexturedPlane(2,1)
  g.map2dAssembly.AddPart(g.mapActor)

  # create spinning earth animation
  animation = animations.RevolveZAnimation(g.textureGlobe)
  iren.AddObserver('TimerEvent', animation.execute)

def loadFile(fileame):
  print("load file ",filename)

#_______________________________________________________________________
# handle keypress events
def KeyPressed(obj,event):

  key = obj.GetKeySym()

  if key == "Up":
    g.level_index-=1
    select_scalar_field(g.sfield_index)
    print("level_index=",g.level_index)

  if key == "Down":
    g.level_index+=1
    select_scalar_field(g.sfield_index)
    print("level_index=",g.level_index)

  if key == "Right":
    set_time_index(g.time_index+1)
    #g.time_index+=1
    #select_scalar_field(g.sfield_index)
    #print("time_index=",g.time_index)

  elif key == "Left":
    set_time_index(g.time_index-1)
    #g.time_index-=1
    #select_scalar_field(g.sfield_index)
    #print("time_index=",g.time_index)

  elif key == "m":
    print("toggle mesh visibility")
    edge_viz = actor.GetProperty().GetEdgeVisibility()
    print(edge_viz)
    if(edge_viz==1):
      property.EdgeVisibilityOff()
    else:
      property.EdgeVisibilityOn()

  elif key == "p":
    print("toggle parallel projection")
    pp = camera.GetParallelProjection()
    if (pp==1):
      camera.ParallelProjectionOff()
    else:
      camera.ParallelProjectionOn()

  else:
    print("key %s" % key)

#_______________________________________________________________________
if __name__ == "__main__":

  app     = QtGui.QApplication(sys.argv)
  window  = MainWindow()
  ren     = window.renderer
  iren    = window.interactor

  # connect controls to event handlers
  window.openAction.triggered.connect(open_a_file)
  g.projection_toolbar = ProjectionToolbar(window)
  g.projection_toolbar.projection_combo.currentIndexChanged.connect(select_map_projection)

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
  iren.AddObserver("KeyPressEvent", KeyPressed, 1.0)

  # create a repeating timer for animations
  #timerID = iren.CreateRepeatingTimer(100)

  sys.exit(app.exec_())

