# https://www.youtube.com/watch?v=-_z2RPAH0Qk -> Python GUI Development With PySimpleGUI
import PySimpleGUI as sg
import os.path
from tifffile import tifffile
import numpy as np
import base64
import io
from PIL import Image
import cv2
from scipy.ndimage import  affine_transform
from skimage.transform import resize
import time

import Code.Helper as Helper
from Code.Layout import layout
import Code.O3DSolo as O3DSolo
import Code.O3DMulti as O3DMulti
import Code.VTKSolo as VTKSolo
import Code.VTKMulti as VTKMulti
from Code.Popups import *
from Code.GradientAlgo import registerGradient
from Code.RenderOutput import renderProjection

def mmScale(x):
    return (x-np.min(x))/(np.max(x)-np.min(x))

def showProjection(filename):
    #open image
    image = tifffile.imread(filename)
    volume = resize(image, (image.shape[0]*7, image.shape[1], image.shape[2]), mode='constant')# to do: resize
    print(filename)

    # calculate projection
    sumImage = image[1].copy()
    for i in range(1,len(image)):
        sumImage += image[i]

    # # adjust data type(base64) and values(0-255)
    projection = mmScale(sumImage)*255
    projection = projection.astype("uint8")
    projection = cv2.resize(projection, (256,256))

    print(projection.shape,np.min(projection),np.max(projection))
    im_pil = Image.fromarray(projection)

    with io.BytesIO() as output:
        im_pil.save(output, format="PNG")
        data = output.getvalue()

    im_64 = base64.b64encode(data)

    return volume, im_64

def fastProjection(filename):
    try:
        #open image
        image = tifffile.imread(filename)
        print(filename)

        # calculate projection
        sumImage = image[1]
        for i in range(1,len(image)):
            sumImage += image[i]

        # # adjust data type(base64) and values(0-255)
        projection = mmScale(sumImage)*255
        projection = projection.astype("uint8")
        projection = cv2.resize(projection, (256,256))

        print(projection.shape,np.min(projection),np.max(projection))
        im_pil = Image.fromarray(projection)

        with io.BytesIO() as output:
            im_pil.save(output, format="PNG")
            data = output.getvalue()

        im_64 = base64.b64encode(data)
        return im_64
    except Exception as e:
        print("\nERROR: ",e,"\n")
        image = cv2.imread(filename)
        image = cv2.resize(image, (256,256))
        return makeStream(image)




def loadVolume(filename, xDim, yDim, zDim):#, xDim, yDim, zDim
    #load the volume for the 3D Viewer
    print("load Volume")
    print(xDim, yDim, zDim)
    print(filename)
    volume = tifffile.imread(filename)
    zScale = int(float(zDim)/float(xDim))
    print("zScale: ",  zScale)
    print("volume Shape",volume.shape)

    return volume

def showProjection(filename):
    try:
        #open image 3D
        image = tifffile.imread(filename)
        volume = resize(image, (image.shape[0]*7, image.shape[1], image.shape[2]), preserve_range=True, mode='constant')# to do: resize
        print(filename)

        # calculate projection
        sumImage = image[1]
        for i in range(1,len(image)):
            sumImage += image[i]

        # # adjust data type(base64) and values(0-255)
        projection = mmScale(sumImage)*255
        projection = projection.astype("uint8")
        projection = cv2.resize(projection, (256,256))

        print(projection.shape,np.min(projection),np.max(projection))
        im_pil = Image.fromarray(projection)

        with io.BytesIO() as output:
            im_pil.save(output, format="PNG")
            data = output.getvalue()

        im_64 = base64.b64encode(data)

        return volume, im_64
    except Exception as e:
        print("\nERROR: ",e,"\n")
        #open image 2D TODO
        print("open 2D")
        image = Image.open(filename)
        print("pil geladen")
        projection = cv2.resize(image, (256,256))
        print("resized")

        im_pil = Image.fromarray(projection)

        with io.BytesIO() as output:
            im_pil.save(output, format="PNG")
            data = output.getvalue()

        im_64 = base64.b64encode(data)

        return volume, im_64

def makeStream(image):
    im_pil = Image.fromarray(image)
    with io.BytesIO() as output:
        im_pil.save(output, format="PNG")
        data = output.getvalue()

    im_64 = base64.b64encode(data)

    return im_64

def guiInfo(values):
    filename = os.path.join(
        values["-FOLDER-"], values["-FILE LIST-"][0]
    )
    path = values["-FOLDER-"]
    extIn = values["-FILE TYPE-"]
    x = values["-X DIM-"]
    y = values["-Y DIM-"]
    z = values["-Z DIM-"]
    caged = values["-CAGED-"]
    corrected = False
    if float(values["-DEG STEP-"]) == 0:
        corrected = True
    degStep = float(values["-DEG STEP-"])
    start_time = time.time()
    volume = loadVolume(filename, x, y, z)
    noiseThreshold = values["-NOISE THRESH-"]
    zScale = float(z)/float(x)
    return volume, path, extIn, noiseThreshold, zScale, caged, corrected, degStep

def main():
    window = sg.Window("Axial Tomography Viewer and Registration Suite", layout)

    while True:
        event, values = window.read()
        # End programm if user closes window
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        # if Folder name was chosen, make a list of files
        if event == "-FOLDER-":
            folder = values["-FOLDER-"]
            try:
                #get list of files in FOLDER
                file_list = os.listdir(folder)
            except Exception as e:
                print("\nERROR: ",e,"\n")
                file_list = []

            fnames = [
                f
                for f in file_list
                if os.path.isfile(os.path.join(folder, f))
                and f.lower().endswith((".tif",".lsm",".png"))
            ]
            window["-FILE LIST-"].update(fnames, set_to_index = 0)
        elif event == "-FILE LIST-":
            print(values["-FOLDER-"])
            print(values["-FILE LIST-"])
            try:
                filename = os.path.join(
                    values["-FOLDER-"], values["-FILE LIST-"][0]
                )
                window["-TOUT-"].update(filename)
                im_64 = fastProjection(filename)
                window["-IMAGE-"].update(data=im_64)
            except Exception as e:
                print("\nERROR: ",e,"\n")
                # 3D Viewers
        if event == "-3D VIEW VTK-":
            print("VTK Renderer")
            try:
                volume, path, extIn, noiseThreshold, zScale, caged, corrected, degStep = guiInfo(values)
                VTKSolo.volumeRender(volume, noiseThreshold, zScale, caged)
            except Exception as e:
                print("\nERROR: ",e,"\n")
                print("3D Viewer could not be loaded.")
        elif event == "-3D VIEW VTK Multi-":
            print("VTK Multi Renderer")
            try:
                volume, path, extIn, noiseThreshold, zScale, caged, corrected, degStep = guiInfo(values)
                print(path)
                VTKMulti.volumeRender(path, extIn, noiseThreshold, zScale, caged, corrected, degStep)
            except Exception as e:
                print("\nERROR: ",e,"\n")
                print("3D Viewer could not be loaded.")

        elif event == "-3D VIEW O3D-":
            try:
                volume, path, extIn, noiseThreshold, zScale, caged, corrected, degStep = guiInfo(values)
                O3DSolo.pointcloudRender(volume, noiseThreshold, zScale, caged)
            except Exception as e:
                print("\nERROR: ",e,"\n")
                print("3D Viewer could not be loaded.")
        elif event == "-3D VIEW O3D Multi-":
            try:
                volume, path, extIn, noiseThreshold, zScale, caged, corrected, degStep = guiInfo(values)
                print(path)
                O3DMulti.pointcloudRender(path, extIn, noiseThreshold, zScale, caged, corrected, degStep)
            except Exception as e:
                print("\nERROR: ",e,"\n")
                print("3D Viewer could not be loaded.")
        # Registration Methods
        if event == "-GRADIENT-":
            print("GRADIENT")
            try:
                settings = popupGradient()
                window["-INFO-"].update(settings)
                print("\nSettings")
                settings = convertGradientAns(settings[1], values)
                print(settings)
                text = registerGradient(cycle=settings.cycle,
                                        gradient=settings.algorithm,
                                        metric=settings.metric,
                                        multi=settings.multiscale,
                                        lr=settings.lr,
                                        epochs=settings.epochs,
                                        isotropic=settings.isotropie,
                                        graph=settings.graph,
                                        turnback=settings.turnback,
                                        path=settings.folderIn,
                                        dims = settings.dims,
                                        folder=settings.folderOut,
                                        extIn=settings.extIn,
                                        extOut=settings.extOut,
                                        filename=settings.savename,
                                        degStep=settings.degStep,
                                        samplingPercent=settings.samplingPercent)
                window["-INFO-"].update(text)
            except Exception as e:
                print("\nERROR: ",e,"\n")
                print("error")
                window["-INFO-"].update("Bei dem Versuch eine Registrierung zu starten\nbzw. durchzuführen gab es einen Fehler.")

        elif event == "-MARKER-":
            print("MARKER")
            settings = popupMarker()
            window["-INFO-"].update(settings)
        elif event == "-RL-":
            print("Reinforcement Learning")
            settings = popupRL()
            window["-INFO-"].update(settings)
        elif event == "-FOURIER-":
            print("Fourier")
            settings = popupFourier()
            window["-INFO-"].update(settings)
        if event == "-RENDER-":
            print("Render")
            try:
                settings = popupRender()
                print(settings[1])
                settings = convertRenderAns(settings[1], values)
                volume, path, extIn, noiseThreshold, zScale, caged, corrected, degStep = guiInfo(values)
                text,imageComb = renderProjection(inPath=settings.folderIn,
                                 outPath=settings.folderOut,
                                 savename=settings.savename,
                                 extIn=settings.extIn,
                                 dims=settings.dims,
                                 downscale=1,
                                 rot_x=settings.rotX,
                                 rot_y=settings.rotY,
                                 rot_z=settings.rotZ,
                                 zoom=settings.zoom,
                                 saveSingle=True,
                                 degStep = float(values["-DEG STEP-"]),
                                 corrected=corrected
                                )
                window["-INFO-"].update(text)

                window["-IMAGE-"].update(data=makeStream(imageComb))
            except Exception as e:
                print("\nERROR: ",e,"\n")
                print("Error")


    window.close()

if __name__ == '__main__':
    main()
