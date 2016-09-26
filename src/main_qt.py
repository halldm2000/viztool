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
  update_sfield(update_range = False)
#select_scalar_field(g.sfield_index)

#_______________________________________________________________________
def increment_time_index():
  set_time_index(g.time_index+1)

#_______________________________________________________________________
def decrement_time_index():
  set_time_index(g.time_index-1)

#_______________________________________________________________________
def update_sfield(update_range):

  field2d = None

  if(g.sfield.ndim ==4):
    field2d = g.sfield[g.time_index,g.level_index,:,:]
  
  if(g.sfield.ndim ==3):
    field2d = g.sfield[g.time_index,:,:]

  g.dataGlobe.set_scalar_field(field2d)
  g.map3dActor.set_scalar_field(field2d,update_range)

  return field2d

#_______________________________________________________________________
def select_scalar_field(i):

  global window,ren

  # identify selected field
  g.sfield_index = i
  text    = g.fields_toolbar.scalars_combo.itemText(i)
  varname = g.fields_toolbar.scalars_combo.itemData(i)

  if(i == 0):
    # no scalar field selected, hide data globe
    g.dataGlobe.VisibilityOff()
    g.scalarBar.VisibilityOff()

  else:
    # ensure data globe is visible
    g.dataGlobe.VisibilityOn()
    g.scalarBar.VisibilityOn()
    g.sfield   = g.dataset.variables[varname]
    field2d = update_sfield(update_range =True)

  window.renwin.Render()
  window.vtkWidget.setFocus()
  camera = ren.GetActiveCamera()
  camera.SetClippingRange(0.1,1000)

#_______________________________________________________________________
def select_vector_field(i):
  pass

#_______________________________________________________________________
def select_map_projection(i):

  projection = g.projection_toolbar.projection_combo.itemData(i)
  print("projection=",projection)
  camera = ren.GetActiveCamera()

  # hide all vtk assemblies, then show the right one
  for assembly in g.vtk_assemblies:
    assembly.VisibilityOff()

  if(projection=="globe"):

    g.globeAssembly.VisibilityOn()

    if(g.dataGlobe !=None):
      g.dataGlobe.VisibilityOn()

    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    ren.ResetCamera()
    camera.Zoom(1.5)

  elif(projection=="map2d"):

    g.map2dAssembly.VisibilityOn()
    iren.SetInteractorStyle(vtk.vtkInteractorStyleImage())
    camera.SetPosition(0,0,7)
    camera.SetViewUp(0,1,0)
    ren.ResetCamera()
    camera.Zoom(1.5)

  elif(projection=="map3d"):

    g.map3dAssembly.VisibilityOn()
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    ren.ResetCamera()
    camera.Zoom(1.5)

    print("camera pos=",camera.GetPosition())

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

  # construct toolsbars needed for netcdf data
  g.fields_toolbar = NCToolbar  (window,g.dataset)
  g.time_toolbar   = TimeToolbar(window)

  # hook up widgets to event handlers
  g.fields_toolbar.scalars_combo.currentIndexChanged.connect(select_scalar_field)
  g.fields_toolbar.vectors_combo.currentIndexChanged.connect(select_vector_field)

  g.time_toolbar.nextButton.clicked.connect(increment_time_index)
  g.time_toolbar.previousButton.clicked.connect(decrement_time_index)

  # create a lat-lon surface for the 3d map assembly
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

  g.map3dActor = tobs.LatLonSurface(lats,lons)
  g.map3dAssembly.AddPart(g.map3dActor)
  
  # add scalar bar actor
  g.scalarBar = vtk.vtkScalarBarActor()
  g.scalarBar.SetOrientationToVertical()
  g.scalarBar.SetLookupTable(g.lut)
  g.scalarBar.SetWidth(0.08)
  g.scalarBar.SetPosition(0.90,0.1)
  g.scalarBar.SetTextPositionToPrecedeScalarBar()
  ren.AddActor(g.scalarBar)

  # trigger "select_scalar_field" method
  g.fields_toolbar.scalars_combo.setCurrentIndex(1)

#_______________________________________________________________________
def create_default_scene():
  global ren, iren

  # make globe assembly
  g.textureGlobe = tobs.TexturedSphere(0.99,"../images/earth.jpg")
  g.globeAssembly = vtk.vtkAssembly()
  g.globeAssembly.AddPart(g.textureGlobe)
  ren.AddActor(g.globeAssembly)
  g.vtk_assemblies.append(g.globeAssembly)

  # make map2d assembly
  g.map2dAssembly = vtk.vtkAssembly()
  g.map2dAssembly.VisibilityOff()
  g.map2dActor = tobs.TexturedPlane(2,1)
  g.map2dAssembly.AddPart(g.map2dActor)
  ren.AddActor(g.map2dAssembly)
  g.vtk_assemblies.append(g.map2dAssembly)

  # make map3d assembly
  g.map3dAssembly = vtk.vtkAssembly()
  g.map3dAssembly.VisibilityOff()
  #g.map3dActor = tobs.TexturedPlane(2,1)
  #g.map3dAssembly.AddPart(g.map3dActor)
  ren.AddActor(g.map3dAssembly)
  g.vtk_assemblies.append(g.map3dAssembly)

  # create spinning earth animation
  animation = animations.RevolveZAnimation(g.textureGlobe)
  animation.angularSpeed = 360.0/100.0
  iren.AddObserver('TimerEvent', animation.execute)

#_______________________________________________________________________
def KeyPressed(obj,event):

  # handle keypress events
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

  elif key == "Left":
    set_time_index(g.time_index-1)

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

  # make app, window, renderer and interactor
  app     = QtGui.QApplication(sys.argv)
  window  = MainWindow()
  ren     = window.renderer
  iren    = window.interactor

  # connect widgets with event handlers
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
  timerID = iren.CreateRepeatingTimer(500)

  sys.exit(app.exec_())

