import vtk

class TexturedSphere:
  
    def __init__(self,radius,fileName):

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

      # create a vtk actor using the polygons and texure
      actor = vtk.vtkActor()
      actor.SetMapper(mapper)
      actor.SetTexture(texture)
      actor.RotateX(90)
      
      # set default actor properties of the textured sphere
      property = actor.GetProperty()
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
      self.actor    = actor
      self.property = property
