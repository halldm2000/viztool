#!/usr/bin/env pythonw
# goal: netcdf + vtk

import vtk
from math import *
import numpy as np
from netCDF4 import Dataset
from vtk.util.colors import *

#_______________________________________________________________________
def sphere2cart(lat,lon,R):
  z   = R*sin(lat)
  r   = R*cos(lat)
  x   = r*cos(lon)
  y   = r*sin(lon)
  p   = [x,y,z]
  return p

#_______________________________________________________________________
def read_netcdf_header(ncfile):
  dataset = Dataset(ncfile, 'r')
  print(dataset)
  return dataset
  
#_______________________________________________________________________
def make_latlon_surface(lats,lons,field2d):

  nlon      = lons.size
  nlat      = lats.size
  pts       = vtk.vtkPoints()
  verts     = vtk.vtkCellArray()
  vals      = vtk.vtkDoubleArray()
  quads     = vtk.vtkCellArray()
  stride    = 1                   # number of lats to skip
  R         = 1.0                 # radius of sphere
  fieldMin  = np.amin(field2d)
  fieldMax  = np.amax(field2d)

  vals.SetName('values')

  # create color lookup table
  nc  = vtk.vtkNamedColors()
  lut = vtk.vtkLookupTable()
  lut.Build()
  lut.SetTableRange(fieldMin,fieldMax)
  lut.SetHueRange(0.0,1.0)
  #lut.SetSaturationRange(1,1);
  lut.SetValueRange(1.0,1.0);

  for i in range(0,nlon-1,stride):

    i1 = i
    i2 = (i+stride)

    if(i2>nlon-1):
      i2 = 0

    lon1 = lons[i1]*pi/180.0
    lon2 = lons[i2]*pi/180.0
    print("add points at lon ",lon1)

    for j in range(0,nlat-stride,stride):

      j1 = j
      j2 = (j+stride)

      lat1 = lats[j1]*pi/180.0
      lat2 = lats[j2]*pi/180.0

      print("lat1=",lat1," lat2=",lat2)

      p1  = sphere2cart(lat1,lon1,1.0)
      id1 = pts.InsertNextPoint(p1)
      verts.InsertNextCell(1)
      verts.InsertCellPoint(id1)
      vals.InsertNextValue(field2d[j1,i1]  )

      p2  = sphere2cart(lat2,lon1,1.0)
      id2 = pts.InsertNextPoint(p2)
      verts.InsertNextCell(1)
      verts.InsertCellPoint(id2)
      vals.InsertNextValue(field2d[j2,i1]  )

      p3  = sphere2cart(lat2,lon2,1.0)
      id3 = pts.InsertNextPoint(p3)
      verts.InsertNextCell(1)
      verts.InsertCellPoint(id3)
      vals.InsertNextValue(field2d[j2,i2]  )

      p4  = sphere2cart(lat1,lon2,1.0)
      id4 = pts.InsertNextPoint(p4)
      verts.InsertNextCell(1)
      verts.InsertCellPoint(id4)
      vals.InsertNextValue(field2d[j1 ,i2]  )

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
  ptMapper.SetScalarRange(fieldMin,fieldMax)
  ptMapper.SetScalarModeToUsePointData()
  ptMapper.SetScalarVisibility(1)
  ptActor=vtk.vtkActor()
  ptActor.SetMapper(ptMapper)
  ptActor.GetProperty().SetPointSize(1)
  ptActor.GetProperty().SetEdgeColor(0,0,0)
  ptActor.GetProperty().EdgeVisibilityOn()
  ptActor.GetProperty().SetLineWidth(0.1)
  ptActor.GetProperty().SetDiffuse(1);
  ptActor.GetProperty().SetSpecular(0.1)
  ptActor.GetProperty().SetSpecularPower(50.0)
  ptActor.GetProperty().SetAmbient(0.05);
  ptActor.GetProperty().SetOpacity(1);
  ptActor.GetProperty().SetInterpolationToPhong();
  ptActor.RotateX(90)

  return ptActor

#_______________________________________________________________________
def read_netcdf_latlon(ncfile, ren):

  # open and read netcdf file
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
  lut.SetHueRange(0.0,1.0)
  #lut.SetSaturationRange(1,1);
  lut.SetValueRange(1.0,1.0);

  vals = vtk.vtkDoubleArray()
  vals.SetName('values')
  quads = vtk.vtkCellArray()

  stride  = 4  # number of lats to skip
  R       = 1.0 # radius of sphere
  for i in range(0,nlon-1,stride):

    i1 = i
    i2 = (i+stride)

    if(i2>nlon-1):
      i2 = 0

    lon1 = lons[i1]*pi/180.0
    lon2 = lons[i2]*pi/180.0
    print("add points at lon ",lon1)

    for j in range(0,nlat-stride,stride):

      j1 = j
      j2 = (j+stride)

      lat1 = lats[j1]*pi/180.0
      lat2 = lats[j2]*pi/180.0

      print("lat1=",lat1," lat2=",lat2)

      p1  = sphere2cart(lat1,lon1,1.0)
      id1 = pts.InsertNextPoint(p1)
      verts.InsertNextCell(1)
      verts.InsertCellPoint(id1)
      vals.InsertNextValue(ps[j1,i1]  )

      p2  = sphere2cart(lat2,lon1,1.0)
      id2 = pts.InsertNextPoint(p2)
      verts.InsertNextCell(1)
      verts.InsertCellPoint(id2)
      vals.InsertNextValue(ps[j2,i1]  )

      p3  = sphere2cart(lat2,lon2,1.0)
      id3 = pts.InsertNextPoint(p3)
      verts.InsertNextCell(1)
      verts.InsertCellPoint(id3)
      vals.InsertNextValue(ps[j2,i2]  )

      p4  = sphere2cart(lat1,lon2,1.0)
      id4 = pts.InsertNextPoint(p4)
      verts.InsertNextCell(1)
      verts.InsertCellPoint(id4)
      vals.InsertNextValue(ps[j1 ,i2]  )

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
  ptActor.GetProperty().EdgeVisibilityOn()
  ptActor.GetProperty().SetLineWidth(0.1)
  ptActor.GetProperty().SetDiffuse(1);
  ptActor.GetProperty().SetSpecular(0.1)
  ptActor.GetProperty().SetSpecularPower(50.0)
  ptActor.GetProperty().SetAmbient(0.05);
  ptActor.GetProperty().SetOpacity(1);
  ptActor.GetProperty().SetInterpolationToPhong();
  ptActor.RotateX(90)
  ren.AddActor(ptActor)

  # add scalar bar actor
  scalarBar = vtk.vtkScalarBarActor()
  scalarBar.SetOrientationToVertical()
  scalarBar.SetLookupTable(lut)
  scalarBar.SetWidth(0.1)
  scalarBar.SetPosition(0.85,0.1)
  scalarBar.SetTextPositionToPrecedeScalarBar()
  ren.AddActor(scalarBar)

  # set background color and camera position
  ren.RemoveAllLights()
  ren.SetBackground (.0,.0,.0)
  ren.SetBackground2(.0,.0,.0)
  ren.SetGradientBackground(1)
  ren.ResetCamera()
  ren.GetActiveCamera().Zoom(1.2)
  ren.AutomaticLightCreationOn()
  ren.TwoSidedLightingOn()
