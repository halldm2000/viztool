import vtk
import time

class RevolveZAnimation:

  def __init__(self,actor):
    self.actor        = actor
    self.angularSpeed = 360.0 / 40.0      # units: dg/sec
    startTime         = time.time()
    self.lastTime     = startTime

  def execute(self,obj,event):
    global dt, camera

    renderer = obj
    renderer.GetRenderWindow().Render()
    currentTime   = time.time()
    dt            = currentTime - self.lastTime
    self.lastTime = currentTime
    self.actor.RotateZ(-dt*self.angularSpeed)

class CameraZoom:

  def __init__(self,camera):
    self.camera       = camera

    self.startTime    = time.time()
    self.endTime      = self.startTime
    self.lastTime     = self.startTime

  def begin(self,factor):
    currentTime   = time.time()

    if(self.endTime > currentTime):
      self.factor   += 0

    else:
      self.startTime  = time.time()
      self.lastTime   = self.startTime
      self.factor     = factor
      self.endTime    = self.startTime + 0.10

      print("start = ",self.factor)

  def execute(self,obj,event):
    currentTime   = time.time()

    if(self.endTime > currentTime):
      renderer = obj
      renderer.GetRenderWindow().Render()
      dt = currentTime - self.lastTime
      self.lastTime = currentTime
      self.camera.Dolly(1.0 + self.factor*dt)
# print("t=",currentTime," endT=",self.endTime," dt=",dt)