import vtk
import random
from math import *
import numpy as np
import globals as g
#_______________________________________________________________________
def sphere2cart(lat,lon,R):
  p = [R*cos(lat)*cos(lon),R*cos(lat)*sin(lon),R*sin(lat)]
  return p

#_______________________________________________________________________
class QuadSphere(vtk.vtkActor):

  def __init__(self,lats,lons):
    vtk.vtkActor.__init__(self)

    nlon      = lons.size
    nlat      = lats.size
    pts       = vtk.vtkPoints()
    verts     = vtk.vtkCellArray()
    self.vals = vtk.vtkDoubleArray()
    quads     = vtk.vtkCellArray()
    stride    = 1                   # number of lats to skip
    R         = 1.0                 # radius of sphere
    fieldMin  = 0 #np.amin(field2d)
    fieldMax  = 1 #np.amax(field2d)

    self.vals.SetName('values')

    self.inds = []

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

        p1  = sphere2cart(lat1,lon1,1.0)
        id1 = pts.InsertNextPoint(p1)
        verts.InsertNextCell(1)
        verts.InsertCellPoint(id1)
        self.vals.InsertNextValue(1)
        self.inds.append([j1,i1])

        p2  = sphere2cart(lat2,lon1,1.0)
        id2 = pts.InsertNextPoint(p2)
        verts.InsertNextCell(1)
        verts.InsertCellPoint(id2)
        self.vals.InsertNextValue(1)
        self.inds.append([j2,i1])

        p3  = sphere2cart(lat2,lon2,1.0)
        id3 = pts.InsertNextPoint(p3)
        verts.InsertNextCell(1)
        verts.InsertCellPoint(id3)
        self.vals.InsertNextValue(1)
        self.inds.append([j2,i2])

        p4  = sphere2cart(lat1,lon2,1.0)
        id4 = pts.InsertNextPoint(p4)
        verts.InsertNextCell(1)
        verts.InsertCellPoint(id4)
        self.vals.InsertNextValue(1)
        self.inds.append([j1,i2])

        quad = vtk.vtkQuad()
        quad.GetPointIds().SetId(0,id1)
        quad.GetPointIds().SetId(1,id2)
        quad.GetPointIds().SetId(2,id3)
        quad.GetPointIds().SetId(3,id4)
        quads.InsertNextCell(quad)

    self.polyData  = vtk.vtkPolyData()
    self.polyData.SetPoints(pts)
    #polyData.SetVerts(verts)
    self.polyData.SetPolys(quads)
    self.polyData.GetPointData().SetScalars(self.vals)
    self.polyData.GetPointData().SetActiveScalars('values')

    self.ptMapper = vtk.vtkPolyDataMapper()
    self.ptMapper.SetInputData(self.polyData)
    self.ptMapper.SetLookupTable(g.lut)
    self.ptMapper.SetScalarRange(fieldMin,fieldMax)
    self.ptMapper.SetScalarModeToUsePointData()
    self.ptMapper.SetScalarVisibility(1)

    self.SetMapper(self.ptMapper)
    property = self.GetProperty()
    property.SetPointSize(1)
    property.SetEdgeColor(1,1,1)
    property.EdgeVisibilityOff()
    property.SetLineWidth(0.1)
    property.SetDiffuse(1);
    property.SetSpecular(0.1)
    property.SetSpecularPower(50.0)
    property.SetAmbient(0.05);
    property.SetOpacity(1);
    property.SetInterpolationToPhong();
    self.RotateX(90)

  #.....................................................................
  def set_scalar_field(self,field2d):

    for i,ind in enumerate(self.inds):
      self.vals.SetValue(i,field2d[ind[0],ind[1]])

    fieldMin  = np.amin(field2d)
    fieldMax  = np.amax(field2d)

    g.lut.SetTableRange(fieldMin,fieldMax)
    self.ptMapper.SetScalarRange(fieldMin,fieldMax)
    self.polyData.Modified();

#_______________________________________________________________________
class DataSphere(vtk.vtkActor):

  def __init__(self,lats,lons):

    vtk.vtkActor.__init__(self)

    nlon = lons.size
    nlat = lats.size

    print("nlat=",nlat," nlon=",nlon)

    # create a sphere source
    source = vtk.vtkSphereSource()
    source.LatLongTessellationOn()
    source.SetCenter(0,0,0)
    source.SetRadius(1.0)
    source.SetThetaResolution(nlon)
    source.SetPhiResolution(nlat)
    source.Update()

    npts = source.GetOutput().GetPoints().GetNumberOfPoints()
    points =source.GetOutput().GetPoints()

    scalars = vtk.vtkFloatArray()
    scalars.SetNumberOfValues(npts)

    for i in range(0,npts-1):
      scalars.SetValue(i, random.random())

    poly = vtk.vtkPolyData()
    poly.DeepCopy(source.GetOutput())
    poly.GetPointData().SetScalars(scalars)

    g.lut.SetTableRange(0,1)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(poly)
    mapper.ScalarVisibilityOn()
    mapper.SetScalarModeToUsePointData()
    mapper.SetColorModeToMapScalars()
    mapper.SetLookupTable(g.lut)

    self.SetMapper(mapper)
    self.GetProperty().SetEdgeColor(1,1,1)
    self.GetProperty().EdgeVisibilityOn()
    self.GetProperty().SetLineWidth(0.1)

#_______________________________________________________________________
class TexturedPlane(vtk.vtkActor):

  def __init__(self,width,height):

    vtk.vtkActor.__init__(self)

    reader = vtk.vtkJPEGReader()
    reader.SetFileName("../images/earth.jpg")

    atext = vtk.vtkTexture()
    atext.SetInputConnection(reader.GetOutputPort())
    atext.InterpolateOn()

    plane = vtk.vtkPlaneSource()
    plane.SetNormal(0, 0, 1)
    plane.SetOrigin(0, 0, 0);
    plane.SetPoint1(width, 0, 0);
    plane.SetPoint2(0, height, 0);
    plane.SetCenter(0, 0, 0);

    warpScalar = vtk.vtkWarpScalar()
    warpScalar.SetInputConnection(plane.GetOutputPort());
    warpScalar.SetScaleFactor(1);
    warpScalar.UseNormalOn();
    warpScalar.SetNormal(0, 0, 1);
    warpScalar.Update();

    planeMapper = vtk.vtkPolyDataMapper()
    planeMapper.SetInputConnection(plane.GetOutputPort())

    self.SetMapper(planeMapper)
    self.SetTexture(atext)

    self.GetProperty().SetAmbient(0.2);
    self.GetProperty().SetEdgeColor(1,1,1)
    self.GetProperty().EdgeVisibilityOn()
    self.GetProperty().SetLineWidth(0.1)

#_______________________________________________________________________
class LatLonSurface(vtk.vtkActor):

  def __init__(self,lats,lons):

    vtk.vtkActor.__init__(self)

    points  = vtk.vtkPoints()
    self.vals = vtk.vtkFloatArray()

    nlon = lons.size
    nlat = lats.size

    scale = 4.0/360.0
    self.inds = []

    for j in range(0,nlat-1):
      for i in range(0,nlon-1):
        x = -2 + lons[i]*scale
        y =  0 + lats[j]*scale
        z =  cos(3.14*x)*sin(3.14*y)
        print("x = ",x,"y = ",y)
        points.InsertNextPoint(x,y,0)
        self.vals.InsertNextValue(z)
        self.inds.append([j,i])

    self.polyData = vtk.vtkPolyData()
    self.polyData.SetPoints(points)
    self.polyData.GetPointData().SetScalars(self.vals)

    delaunay2D = vtk.vtkDelaunay2D()
    delaunay2D.SetInputData(self.polyData)
    delaunay2D.Update()

    self.mapper = vtk.vtkDataSetMapper()
    self.mapper.SetInputConnection(delaunay2D.GetOutputPort())

    self.mapper.SetColorModeToMapScalars()
    self.mapper.SetLookupTable(g.lut)

    self.SetMapper(self.mapper)
    self.GetProperty().SetAmbient(0.2);
    self.GetProperty().SetEdgeColor(1,1,1)
    self.GetProperty().EdgeVisibilityOff()
    self.GetProperty().SetLineWidth(0.1)

  #.....................................................................
  def set_scalar_field(self,field2d,update_range):

    self.min  = np.amin(field2d)
    self.max  = np.amax(field2d)
    self.range= self.max - self.min
    self.mean = (self.max + self.min)/2

    points = self.polyData.GetPoints()

    # set vertical scale
    sv = 0.5/self.range

    for i,ind in enumerate(self.inds):

      val = field2d[ind[0],ind[1]]
      # change surface colors
      self.vals.SetValue(i,val)

      # change geometry
      pt = points.GetPoint(i)
      points.SetPoint(i, pt[0],pt[1],(val-self.mean)*sv)

      if(update_range==True):
        self.mapper.SetScalarRange(self.min,self.max)

    self.polyData.Modified();

#_______________________________________________________________________
class DataSurface(vtk.vtkActor):

  def __init__(self,width,height):

    vtk.vtkActor.__init__(self)

    #reader = vtk.vtkJPEGReader()
    #reader.SetFileName("../images/earth.jpg")

    nlat = 90
    nlon = 180

    myArray = vtk.vtkDoubleArray()
    myArray.SetName('zcoords')
    myArray.SetNumberOfComponents(1)
    myArray.SetNumberOfTuples(nlat*nlon)
    for x in range(0,nlon-1):
      for y in range(0,nlat-1):
        myArray.SetValue( x*nlon + y, random.random() )

    image_data = vtk.vtkImageData()
    image_data.SetDimensions(180,90,1)
    image_data.SetOrigin(0,0,0)
    image_data.SetSpacing(1./90,1./90, 1)
    image_data.SetScalarType(vtk.VTK_DOUBLE)
    image_data.GetPointData().SetScalars(myArray)

    dataMapper = vtk.vtkDataSetMapper()
    dataMapper = vtk.SetInput(image_data)
    dataMapper.ScalarVisibilityOn()

#    atext = vtk.vtkTexture()
#    atext.SetInputConnection(reader.GetOutputPort())
#    atext.InterpolateOn()

#   warpScalar = vtk.vtkWarpScalar()
#    warpScalar.SetInputConnection(plane.GetOutputPort());
#    warpScalar.SetScaleFactor(1);
#    warpScalar.UseNormalOn();
#    warpScalar.SetNormal(0, 0, 1);
#    warpScalar.Update();

#planeMapper = vtk.vtkPolyDataMapper()
#    planeMapper.SetInputConnection(plane.GetOutputPort())

    self.SetMapper(dataMapper)
    #self.SetTexture(atext)

    self.GetProperty().SetAmbient(0.2);
    self.GetProperty().SetEdgeColor(1,1,1)
    self.GetProperty().EdgeVisibilityOn()
    self.GetProperty().SetLineWidth(0.1)

#_______________________________________________________________________
class TexturedSphere(vtk.vtkActor):
  
  def __init__(self,radius,fileName):
    vtk.vtkActor.__init__(self)

    # create a sphere source
    source = vtk.vtkSphereSource()
    source.SetThetaResolution(180)
    source.SetPhiResolution(91)
    source.SetRadius(radius)
    source.SetStartTheta(0)
    source.SetEndTheta(359.99999)

    # read image file
    reader = vtk.vtkJPEGReader()
    reader.SetFileName(fileName)

    # create a texture
    texture = vtk.vtkTexture()
    texture.SetInputConnection(reader.GetOutputPort())

    # create a texture map onto the sphere
    textureMap = vtk.vtkTextureMapToSphere()
    textureMap.SetInputConnection(source.GetOutputPort())
    textureMap.PreventSeamOff()

    # flip the texture to get correct orientation
    transform = vtk.vtkTransformTextureCoords()
    transform.SetInputConnection(textureMap.GetOutputPort())
    transform.FlipSOn()

    # create polygons from transformed texture coordinates
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(transform.GetOutputPort())
    mapper.ScalarVisibilityOn()
    mapper.SetScalarModeToUsePointData()

    # create a vtk actor using the polygons and texure
    self.SetMapper(mapper)
    self.SetTexture(texture)
    self.RotateX(90)
    
    # set default actor properties of the textured sphere
    property = self.GetProperty()
    property.LightingOn()
    property.SetColor(1,1,1)
    property.SetDiffuse(1);
    property.SetSpecular(1)
    property.SetSpecularPower(50.0)
    property.SetAmbient(0.1);
    property.EdgeVisibilityOff()
    property.SetLineWidth(0.5)

    # create instance variables
    self.fileName = fileName
    self.radius   = radius
    self.source   = source
    self.reader   = reader
    self.texture  = texture
    self.mapper   = mapper
    self.property = property
