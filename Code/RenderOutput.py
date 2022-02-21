# Dependencies
import os
import numpy as np
import tifffile
import cv2
from skimage.transform import rescale
from scipy.ndimage import  affine_transform

# main function
def renderProjection(inPath="",
                     outPath="",
                     savename="",
                     extIn=".tif",
                     dims=[1,1,1],
                     downscale=1,
                     rot_x=45,
                     rot_y=45,
                     rot_z=45,
                     zoom=0,
                     saveSingle=True,
                     degStep = 45,
                     corrected=False
                    ):
    '''Docstring'''
    # Import
    filenames = generateFilenames(inPath, extIn)
    angles = [degStep*x for x in range(len(filenames))]
    # Setup of each image
    projList = []
    angleCounter =0
    for filename in filenames:
        # opening the volume
        volume = tifffile.imread(filename)
        if len(volume.shape) == 4:
            volume = volume[:,:,:,0]

        # making them isotropic if necessary
        if volume.shape[0] != volume.shape[1] or downscale != 1:
            volume = realSize(volume, dims[0], dims[1], dims[2], downscale)
        #correct the angle
        if corrected==False:
            volume = applyRotation(volume, rot_x, rot_y, rot_z-angles[angleCounter])
        # apply the rotation
        else:
            volume = applyRotation(volume, rot_x, rot_y, rot_z)
        angleCounter+=1

        # generate the projection
        image = zProjection(volume)

        # zoom if necessary
        if zoom>0:
            image = applyZoom(image, zoom, np.max(volume.shape))
        projList.append(image)

    # generate the color images
    coloredList = colorize(projList)

    if saveSingle:
        i=0
        for image in projList:
            name = os.path.join(outPath,str(i*45)+savename+" degrees_alone"+".png")
            name = name.replace("\\", "/")
            outImg = mmScale(image)*255
            cv2.imwrite(name,outImg.astype("uint8"))
            i+=1

    # generate and save combined images
    whiteCombined = mergeAll(projList)*255
    whiteCombined = whiteCombined.astype("uint8")
    name = os.path.join(outPath,savename+"combined Grey"+".png")
    name = name.replace("\\", "/")
    cv2.imwrite(name,whiteCombined)

    coloredCombined = mergeAll(coloredList)*255
    coloredCombined = coloredCombined.astype("uint8")
    coloredCombined = cv2.cvtColor(coloredCombined, cv2.COLOR_BGR2RGB)
    name = os.path.join(outPath,savename+"combined Color"+".png")
    name = name.replace("\\", "/")
    cv2.imwrite(name,coloredCombined)

    # Antworttext
    text = f"Die Bilder wurden im Ordner {outPath} mit label {savename} gespeichert."
    print(text)
    coloredCombinedSmall = cv2.resize(coloredCombined, (256,256))
    return text, coloredCombinedSmall

# helperfunctions
def generateFilenames(folder, ext):
    fList = []
    print("folder: ", folder)
    for root, directories, filenames in os.walk(folder):
        filenames.sort()
        for filename in filenames:
            # Check for file extension
            if not filename.lower().endswith(ext):
                continue
            fList.append(os.path.join(root,filename))
            print(filename)
    return fList

def zProjection(image3D):
    sumImage = image3D[0]
    for i in range(1, len(image3D)):
        sumImage += image3D[i]
    return sumImage

def realSize(volume, dim_x, dim_y, dim_z, down):
    minDim = np.min([dim_x, dim_y, dim_z])
    xFactor = dim_x/minDim/down
    yFactor = dim_y/minDim/down
    zFactor = dim_z/minDim/down
    resizedVolume = rescale(volume, scale=(zFactor, yFactor, xFactor), mode='reflect')
    return resizedVolume

def applyRotation(volume, rot_x, rot_y, rot_z):
    # zentrumsmatrix
    shiftX, shiftY, shiftZ  = int(volume.shape[0]/2), int(volume.shape[1]/2), int(volume.shape[2]/2)
    MshiftCenter = np.float32([[1,0,0,shiftX],[0,1,0,shiftY],[0,0,1,shiftZ],[0,0,0,1]])

    rotX, rotY, rotZ  = np.radians(rot_x),np.radians(rot_y),np.radians(rot_z)
    MrotX = np.float32([[1,0,0,0],[0,np.cos(rotX),np.sin(rotX),0],[0,-1*np.sin(rotX),np.cos(rotX),0],[0,0,0,1]])
    MrotY = np.float32([[np.cos(rotY),0,-np.sin(rotY),0],[0,1,0,0],[np.sin(rotY),0,np.cos(rotY),0],[0,0,0,1]])
    MrotZ = np.float32([[np.cos(rotZ),-np.sin(rotZ),0,0],[np.sin(rotZ),np.cos(rotZ),0,0],[0,0,1,0],[0,0,0,1]])

    MshiftBack = np.float32([[1,0,0,-shiftX],[0,1,0,-shiftY],[0,0,1,-shiftZ],[0,0,0,1]])

    M = np.linalg.multi_dot([MshiftCenter,MrotX,MrotY,MrotZ,MshiftBack])

    #print(M)
    rotatedVolume = affine_transform(volume,
                                   M,
                                   offset=0.0,
                                   output_shape=(volume.shape),
                                   output=None,
                                   order=1,
                                   mode='constant',
                                   cval=0,
                                   prefilter=True)
    return rotatedVolume

def applyZoom(image, factor, size):
    if factor>91 or factor<0:factor=50;
    margin = int(image.shape[0]*(factor/200))+1
    zoomed = image[margin:-margin,margin:-margin]
    zoomed = cv2.resize(zoomed, (size, size), interpolation=cv2.INTER_NEAREST)#TODO OPtion
    return zoomed


def colorize(imageArray):
    colorizedList = []
    colorList = [[1,1,1],[1,0,0],[0,1,0],[0,0,1],[1,1,0],[0,1,1],[1,0,1],[1,0.5,0]]
    for i in range(len(imageArray)):
        originalImage = imageArray[i].copy()
        colorImage = np.zeros((originalImage.shape[0], originalImage.shape[0],3))
        if colorList[i][0] == 1:
            colorImage[:,:,0] = originalImage
        if colorList[i][1] == 1:
            colorImage[:,:,1] = originalImage
        if colorList[i][1] == 0.5:
            colorImage[:,:,1] = originalImage*0.5
        if colorList[i][2] == 1:
            colorImage[:,:,2] = originalImage

        colorizedList.append(colorImage)
    colorizedList = mmScale(colorizedList)
    return np.asarray(colorizedList)

def mmScale(x):
    return (x-np.min(x))/(np.max(x)-np.min(x))

def mergeAll(imgA):
    mergedImage = imgA[0]
    for i in range(1,len(imgA)-1):
        mergedImage = cv2.addWeighted(mergedImage,(i)/(i+1),imgA[i],1/(i+1),1)
    return mmScale(mergedImage)
