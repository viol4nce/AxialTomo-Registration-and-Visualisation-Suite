# An example from scipy cookbook demonstrating the use of numpy arrays in vtk
# https://kitware.github.io/vtk-examples/site/Python/Utilities/VTKWithNumpy/

import numpy as np
import os
from tifffile import tifffile
from skimage.transform import resize
# noinspection PyUnresolvedReferences
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersGeneral import vtkTransformPolyDataFilter
import vtkmodules.vtkInteractionStyle
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkPiecewiseFunction
from vtkmodules.vtkIOImage import vtkImageImport
from vtkmodules.vtkRenderingCore import (
    vtkColorTransferFunction,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkVolume,
    vtkVolumeProperty
)
from vtkmodules.vtkRenderingVolume import vtkFixedPointVolumeRayCastMapper
# noinspection PyUnresolvedReferences
from vtkmodules.vtkRenderingVolumeOpenGL2 import vtkOpenGLRayCastImageDisplayHelper

import Code.Helper as Helper

def generateVolume(fileN, colorF, zScale, thresh=2, angle=0, caged=False, corrected=False):
    print("\n Filename: \n",fileN)
    volume1 = tifffile.imread(fileN)
    print(volume1.shape)
    if len(volume1.shape) == 4:
        volume1 = volume1[:,:,:,1]
    if caged==True:
        volume1 = Helper.cage(volume1)
    volume1[volume1<thresh] = 0
    data_matrix = volume1.astype("uint8")
    print(data_matrix.shape)
    print(np.min(data_matrix), np.max(data_matrix))
    z_dim, y_dim, x_dim = data_matrix.shape
    print(z_dim, y_dim, x_dim)
    dataImporter = vtkImageImport()
    data_string = data_matrix.tobytes()
    dataImporter.CopyImportVoidPointer(data_string, len(data_string))
    dataImporter.SetDataScalarTypeToUnsignedChar()
    dataImporter.SetNumberOfScalarComponents(1)
    dataImporter.SetDataExtent(0, x_dim-1, 0, y_dim-1, 0, z_dim-1)
    dataImporter.SetWholeExtent(0, x_dim-1, 0, y_dim-1, 0, z_dim-1)
    alphaChannelFunc = vtkPiecewiseFunction()
    alphaChannelFunc.AddPoint(0, 0.0)
    alphaChannelFunc.AddPoint(255, 0.3)
    volumeProperty = vtkVolumeProperty()
    colorFunc = vtkColorTransferFunction()
    colorFunc.AddRGBPoint(colorF[0], colorF[1], colorF[2], colorF[3])
    volumeProperty.SetColor(colorFunc)
    volumeProperty.SetScalarOpacity(alphaChannelFunc)
    volume = vtkVolume()
    volume.SetOrigin((x_dim/2,y_dim/2,z_dim/2))
    if corrected == False:
        volume.RotateX(angle)
    volume.SetScale((1,1,zScale))
    volumeMapper = vtkFixedPointVolumeRayCastMapper()
    volumeMapper.SetInputConnection(dataImporter.GetOutputPort())
    volume.SetMapper(volumeMapper)
    volume.SetProperty(volumeProperty)

    return volume

def volumeRender(path, extIn, noiseThreshold, zScale, caged, corrected, degStep=45):
    colors = vtkNamedColors()
    color1 = [100, 1.0, 1.0, 1.0] # Weiß
    color2 = [100, 1.0, 0.0, 0.0] # Rot
    color3 = [100, 0.0, 1.0, 0.0] # Grün
    color4 = [100, 0.0, 0.0, 1.0] # Blau
    color5 = [100, 0.0, 1.0, 1.0] # Cyan
    color6 = [100, 1.0, 0.0, 1.0] # Magenta
    color7 = [100, 1.0, 1.0, 0.0] # Gelb
    color8 = [100, 1.0, 0.5, 0.0] # Orange
    #Generate Lists
    print("filenames")
    print(path)
    filenames = Helper.generateFilenames(path, extIn)
    print(filenames)
    colorsList = [color1,color2,color3,color4,color5,color6,color7,color8]
    #winkel = -45
    angles = [-degStep*x for x in range(0,len(filenames)) ]

    # With almost everything else ready, its time to initialize the renderer and window, as well as
    #  creating a method for exiting the application
    renderer = vtkRenderer()
    renderWin = vtkRenderWindow()
    renderWin.AddRenderer(renderer)
    renderInteractor = vtkRenderWindowInteractor()
    renderInteractor.SetRenderWindow(renderWin)

    # load all the volumes
    print("volumes")
    for i in range(len(colorsList)):
        volume = generateVolume(filenames[i], colorsList[i%len(colorsList)], zScale, noiseThreshold,angles[i],caged,corrected)
        renderer.AddVolume(volume)
    print("volumes Generated")
    renderer.SetBackground(colors.GetColor3d("Black"))

    # ... and set window size.
    renderWin.SetSize(600, 600)
    renderWin.SetWindowName('VTKWithNumpy')

    # A simple function to be called when the user decides to quit the application.
    def exitCheck(obj, event):
        if obj.GetEventPending() != 0:
            obj.SetAbortRender(1)

    # Tell the application to use the function as an exit check.
    renderWin.AddObserver("AbortCheckEvent", exitCheck)

    renderInteractor.Initialize()
    # Because nothing will be rendered without any input, we order the first render manually
    #  before control is handed over to the main-loop.
    renderWin.Render()
    renderInteractor.Start()
