#!/usr/bin/env pythonw
 
import sys
import vtk
from PyQt4 import QtCore, QtGui
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from gui import MainWindow
import textured_objects as tobs
import animations

if __name__ == "__main__":

  app     = QtGui.QApplication(sys.argv)
  window  = MainWindow()
  ren     = window.renderer
  iren    = window.interactor

  # create textured sphere to represent the Earth
  earthSphere = tobs.TexturedSphere(0.99,"../images/earth.jpg")
  ren.AddActor(earthSphere.actor)

  # set camera and lighting attributes
  ren.ResetCamera()
  ren.GetActiveCamera().Zoom(1.5)
  ren.SetLightFollowCamera(0)
  ren.TwoSidedLightingOn()

  # start tracking input from vtk widget in window
  iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
  iren.Initialize()

  # create a repeating timer event
  timerID = iren.CreateRepeatingTimer(20)

  # create spinning earth animation
  animation = animations.RevolveZAnimation(earthSphere.actor)
  iren.AddObserver('TimerEvent', animation.execute)

  sys.exit(app.exec_())

