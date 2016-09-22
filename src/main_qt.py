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
  #print("text=",text," varname=",varname)
  field = g.dataset.variables[varname]

  if(field.ndim ==4):
    field2d = field[g.time_index,g.level_index,:,:]
  
  if(field.ndim ==3):
    field2d = field[g.time_index,:,:]

  g.globe.set_scalar_field(field2d)
  window.renwin.Render()
  window.vtkWidget.setFocus()
#_______________________________________________________________________
def select_vector_field(i):
  pass

#_______________________________________________________________________
def select_map_projection(i):

  projection = g.fields_toolbar.projection_combo.itemData(i)
  print("projection=",projection)
  
  if(projection=="globe"):
    g.map.VisibilityOff()
    g.globe.VisibilityOn()

  elif(projection=="map"):
    g.globe.VisibilityOff()
    g.map.VisibilityOn()

  window.renwin.Render()

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
  g.time_toolbar   = TimeToolbar(window,g.dataset)

  # hook up buttons and comboboxes
  g.fields_toolbar.scalars_combo.currentIndexChanged.connect(select_scalar_field)
  g.fields_toolbar.vectors_combo.currentIndexChanged.connect(select_vector_field)
  g.fields_toolbar.projection_combo.currentIndexChanged.connect(select_map_projection)

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

  # create geometry from lat lon coords
  ren.RemoveAllViewProps();

  g.globe = tobs.QuadSphere(lats,lons)
  ren.AddActor(g.globe)

  g.map = tobs.DataPlane(lats,lons)
  g.map.VisibilityOff()
  ren.AddActor(g.map)

  # add scalar bar actor
  scalarBar = vtk.vtkScalarBarActor()
  scalarBar.SetOrientationToVertical()
  scalarBar.SetLookupTable(g.lut)
  scalarBar.SetWidth(0.08)
  scalarBar.SetPosition(0.90,0.1)
  scalarBar.SetTextPositionToPrecedeScalarBar()
  ren.AddActor(scalarBar)

  select_scalar_field(g.sfield_index)


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
  iren.AddObserver("KeyPressEvent", KeyPressed, 1.0)

  # create a repeating timer for animations
  #timerID = iren.CreateRepeatingTimer(100)

  sys.exit(app.exec_())

