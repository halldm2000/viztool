#!/usr/bin/env pythonw
# goal: netcdf + vtk

import vtk
import time
from math import *
import numpy as np
from netCDF4 import Dataset
from vtk.util.colors import *

import textured_objects as tobs
import animations

def sphere2cart(lat,lon,R):
  z   = R*sin(lat)
  r   = R*cos(lat)
  x   = r*cos(lon)
  y   = r*sin(lon)
  p   = [x,y,z]
  return p

dt = 10 # time between update events

# create renderer, window, and interactor
ren     = vtk.vtkRenderer()
renWin  = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)

# create textured sphere to represent the Earth
earthSphere = tobs.TexturedSphere(0.99,"../images/earth.jpg")
ren.AddActor(earthSphere.actor)

# open and read netcdf file
ncfile = "/Users/dhall/build/halldm2000_homme_dcmip12_test3.1_release/tests_dcmip/dcmip2012_test3.1_nonhydrostatic_gravity_waves/movies/dcmip2012_test31.nc"

dataset = Dataset(ncfile, 'r')
print(dataset)

lons    = dataset.variables['lon']
lats    = dataset.variables['lat']
ps_var  = dataset.variables['ps' ]
nlon    = lons.size
nlat    = lats.size
pts     = vtk.vtkPoints()
verts   = vtk.vtkCellArray()

ps = ps_var[2,:,:]-ps_var[1,:,:]
print(ps)

psMin = np.amin(ps)
psMax = np.amax(ps)
print("psMin",psMin)
print("psMax",psMax)

# create color lookup table
nc  = vtk.vtkNamedColors()
lut = vtk.vtkLookupTable()
lut.Build()
lut.SetTableRange(psMin,psMax)
lut.SetHueRange(0.0,0.0)
#lut.SetSaturationRange(1,1);
lut.SetValueRange(1.0,0.0);

vals = vtk.vtkDoubleArray()
vals.SetName('values')
quads = vtk.vtkCellArray()

stride  = 6  # number of lats to skip
R       = 1.0 # radius of sphere
for i in range(0,nlon-1,stride):

  i1 = i%nlon
  i2 = (i+stride)%nlon

  lon1 = lons[i1]*pi/180.0
  lon2 = lons[i2]*pi/180.0
  print("add points at lon ",lon1)

  for j in range(0,nlat-1,stride):

    j1 = j%nlat
    j2 = (j+stride)%nlat
    lat1 = lats[j1]*pi/180.0
    lat2 = lats[j2]*pi/180.0

    p1  = sphere2cart(lat1,lon1,1.0)
    id1 = pts.InsertNextPoint(p1)
    verts.InsertNextCell(1)
    verts.InsertCellPoint(id1)
    vals.InsertNextValue(ps[j   ,i]  )

    p2  = sphere2cart(lat2,lon1,1.0)
    id2 = pts.InsertNextPoint(p2)
    verts.InsertNextCell(1)
    verts.InsertCellPoint(id2)
    vals.InsertNextValue(ps[j+1  ,i]  )

    p3  = sphere2cart(lat2,lon2,1.0)
    id3 = pts.InsertNextPoint(p3)
    verts.InsertNextCell(1)
    verts.InsertCellPoint(id3)
    vals.InsertNextValue(ps[j+1  ,i+1]  )

    p4  = sphere2cart(lat1,lon2,1.0)
    id4 = pts.InsertNextPoint(p4)
    verts.InsertNextCell(1)
    verts.InsertCellPoint(id4)
    vals.InsertNextValue(ps[j  ,i+1]  )

    quad = vtk.vtkQuad()
    quad.GetPointIds().SetId(0,id1)
    quad.GetPointIds().SetId(1,id2)
    quad.GetPointIds().SetId(2,id3)
    quad.GetPointIds().SetId(3,id4)
    quads.InsertNextCell(quad)

polyData  = vtk.vtkPolyData()
polyData.SetPoints(pts)
#polyData.SetVerts(verts)
polyData.SetPolys(quads)
polyData.GetPointData().SetScalars(vals)
polyData.GetPointData().SetActiveScalars('values')
ptMapper = vtk.vtkPolyDataMapper()
ptMapper.SetInputData(polyData)
ptMapper.SetLookupTable(lut)
ptMapper.SetScalarRange(psMin,psMax)
ptMapper.SetScalarModeToUsePointData()
ptMapper.SetScalarVisibility(1)
ptActor=vtk.vtkActor()
ptActor.SetMapper(ptMapper)
ptActor.GetProperty().SetPointSize(1)
ptActor.GetProperty().SetEdgeColor(0,0,0)
ptActor.GetProperty().EdgeVisibilityOff()
ptActor.GetProperty().SetLineWidth(0.1)
ptActor.GetProperty().SetDiffuse(1);
ptActor.GetProperty().SetSpecular(0.1)
ptActor.GetProperty().SetSpecularPower(50.0)
ptActor.GetProperty().SetAmbient(0.05);
ptActor.GetProperty().SetOpacity(0.90);
ptActor.GetProperty().SetInterpolationToPhong();
ren.AddActor(ptActor)

# set background color and camera position
ren.SetBackground(.0, .0, .0)
ren.SetBackground2(.0,.0,.0)
ren.SetGradientBackground(1)
ren.ResetCamera()
ren.GetActiveCamera().Zoom(1.2)
ren.SetLightFollowCamera(0)
ren.AutomaticLightCreationOff()
ren.TwoSidedLightingOn()

# set window size and render it
renWin.SetSize(600, 600)
renWin.Render()

# add light
light1 = vtk.vtkLight()
light1.SetDiffuseColor(1,1,1);
light1.SetAmbientColor(1,1,1);
light1.SetSpecularColor(1,1,1);
light1.SetDirectionAngle(23.5,-45.0)
light1.PositionalOff()
ren.AddLight(light1)

# set camera
camera = ren.GetActiveCamera()
camera.SetViewUp(0.0,1.0,0.0)
camera.SetPosition(0,0,7.0)

# set interactor
interactor    = vtk.vtkRenderWindowInteractor()
interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
interactor.SetRenderWindow(renWin)

# add scalar bar actor
scalarBar = vtk.vtkScalarBarActor()
scalarBar.SetOrientationToVertical()
scalarBar.SetLookupTable(lut)
scalarBar.SetWidth(0.1)
scalarBar.SetPosition(0.85,0.1)
scalarBar.SetTextPositionToPrecedeScalarBar()
ren.AddActor(scalarBar)

# handle keypress events
def KeyPressed(obj,event):
  key = obj.GetKeySym()

  if key == "Up":
    print("Up")

  if key == "m":

    print("toggle mesh visibility")
    edge_viz = actor.GetProperty().GetEdgeVisibility()
    print(edge_viz)
    if(edge_viz==1):
      property.EdgeVisibilityOff()
    else:
      property.EdgeVisibilityOn()

  if key == "p":

    print("toggle parallel projection")
    pp = camera.GetParallelProjection()
    if (pp==1):
      camera.ParallelProjectionOff()
    else:
      camera.ParallelProjectionOn()

  else:
    print("key %s" % key)

def MouseWheelForward(obj,event):
  global camera, zoomAnimation
  renderer = obj
  print("mousewheel forward event.") # camera position = "+str(camera.GetPosition()))
  camera.SetClippingRange(0.1,100)
  zoomAnimation.begin(1.0)

def MouseWheelBackward(obj,event):
  global camera
  print("mousewheel backward event.")# camera position = "+str(camera.GetPosition()))
  renderer = obj
  camera.SetClippingRange(0.1,100)
  zoomAnimation.begin(-1.0)

# add event observers
#interactor.RemoveObservers("MouseWheelForwardEvent")
#interactor.RemoveObservers("MouseWheelBackwardEvent")
interactor.AddObserver("KeyPressEvent", KeyPressed, 1.0)
interactor.AddObserver("MouseWheelForwardEvent", MouseWheelForward)
interactor.AddObserver("MouseWheelBackwardEvent", MouseWheelBackward)
interactor.Initialize()

# init animations
animation = animations.RevolveZAnimation(earthSphere.actor)
interactor.AddObserver('TimerEvent', animation.execute)

#zoomAnimation = animations.CameraZoom(camera)
#interactor.AddObserver('TimerEvent', zoomAnimation.execute)

# create a repeating timer event
timerID = interactor.CreateRepeatingTimer(dt)
startTime = time.time()

interactor.Start()
