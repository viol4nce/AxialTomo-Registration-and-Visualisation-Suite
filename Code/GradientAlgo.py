import SimpleITK as sitk
from tifffile import tifffile
import matplotlib.pyplot as plt
import cv2
import numpy as np
import os
import time

def registerGradient(cycle="first", gradient="GD", metric="MI", multi=True,
                    lr=0.1, epochs=1e3, isotropic=True, graph=False,
                    turnback=False, path="Input", dims = [1., 1., 1.],
                    folder="Output", extIn=".tif",
                    extOut=".tif", filename="Registration", degStep=45.0, samplingPercent=1.0):
    '''
    This function applies the Gradient based Registration from the SimpleITK
    Toolbox with the Parameters provided by for example GUI.
    it also handles saving of the output data.
    An infotext of the optimization process is returned.
    Parameters:
    cycle: ("first", "next")    Determines the Registration paradigm:
                                first:
                                next:
    gradient:   ("GD","ETC")    Determines the Optimizer:
                                GD: Gradient Descent
                                ETC: following soon
    metric: ("MI", "MSE")   Determines the Metric of the Optimization:
                            MI: Mutual Information
                            MSE: Mean Squared Error
    multi: (bool)           Determines if multi-resolution is used.
    lr: (float)     Learning rate of the Optimizer.
    epochs: (int)   Amount of maximum iterations of the Optimizer.
    isotropic:  (bool)  True, if all the data should be resampled to an
                        isometric Volume.
                        Easier handling of the output data but the process
                        takes longer and requieres more memory.
    graph:  (bool)  True, if graphs of the registration process should be
                    generated and saved in the output folder.
                    This causes a significant slowdown of the process
    turnback:   (bool)  True, if the output data should be turned back multiples
                        of 45° to match the space of the respective input view.
    path:    (string)   Directory where the input is stored.
    dims:   ([float, float, float]) Physical dimensions of the input data in um.
    folder: (string)    Directory where the output is saved.
    extIn:  (".tif",".lsm",".raw") Filetype of the input data.
    extOut: (".tif",".lsm",".raw") Filetype of the output data.
    filename:   (string)    Unique part of the output filename.
    degStep:   (float)    Angle Difference between the aquisitions.
    samplingPercent: (float)    Determins The Amount of Voxels that are used to
                                calculate the gradient.
    '''
    # load the data
    startTime = time.time()
    data = loadData(path, extIn, dims, isotropic, degStep)
    loadingDuration = "\nLoading duration {} s".format(time.time() - startTime)
    print(loadingDuration);startTime = time.time()


    # chose paradigm
    if cycle == "first":
        output, cycleText, graphData, transformData = registerToFirst(data, gradient, metric, multi, lr, epochs, graph, samplingPercent)
    elif cycle == "next":
        output, cycleText, graphData, transformData = registerToNext(data, gradient, metric, multi, lr, epochs, graph, samplingPercent)
    else:
        return "This Paradigm is not supported!\nTry first or next"

    # Info Text for logfile
    infoText1 = logfileHeader(cycle, gradient, metric, multi, lr, epochs,isotropic, graph, turnback, path, dims, folder, extIn,extOut, filename, degStep, samplingPercent)
    infoText1 += cycleText


    registrationDuration = "\nRegistration duration {} s".format(time.time() - startTime)
    print(registrationDuration);startTime = time.time()

    # save data
    infoText = infoText1+loadingDuration+registrationDuration
    infoText2 = saveData(output, infoText, graph, graphData, transformData, folder, filename, turnback, extOut, degStep, isotropic)

    savingDuration = "\nSaving duration {} s".format(time.time() - startTime)
    print(savingDuration);startTime = time.time()
    infoText += infoText2+savingDuration
    print(infoText)
    return infoText

def logfileHeader(cycle, gradient, metric, multi, lr, epochs,
                        isotropic, graph, turnback, path, dims, folder, extIn,
                        extOut, filename, degStep, samplingPercent):
    '''This Generates the Header for the Logfile'''
    header = "This is the logfile for a gradient registration with itk."
    try:
        now = time.asctime()
    except Exception as e:
        print("\nERROR: ",e,"\n")
        now = "ERROR with the time library"
    header += f"\nStarting Time: {now}"
    header += f"\nFollowing Parameters were used:"
    header += f"\n  cycle: {cycle}"
    header += f"\n  degStep: {degStep}"
    header += f"\n  gradient: {gradient}"
    header += f"\n  metric: {metric}"
    header += f"\n  multiscale: {multi}"
    header += f"\n  learning rate: {lr}"
    header += f"\n  epoches: {epochs}"
    header += f"\n  isotropic: {isotropic}"
    header += f"\n  graph: {graph}"
    header += f"\n  turnback: {turnback}"
    header += f"\n  input folder: {path}"
    header += f"\n  dimensions: {dims}"
    header += f"\n  output folder: {folder}"
    header += f"\n  input filetype: {extIn}"
    header += f"\n  output filetype: {extOut}"
    header += f"\n  savename: {filename}"
    header += f"\n  samplingPercent: {samplingPercent}"
    header += "\n##############################################################"
    return header


def saveData(output, infoText1, graph, graphData, transformData, folder, filename, turnback, extOut, degStep, isotropic):
    '''
    Saving the data with the chosen parameters.
    '''
    # saving the transformed volumes
    try:
        if turnback:
            output = turnbackResample(output, degStep)
        for i in range(len(output)):
            savename = os.path.join(folder,str(i)+"_"+filename+extOut)
            savename = savename.replace("\\", "/")#This line is necessary beacause of exe build issues with cx_freeze
            sitk.WriteImage(output[i], savename)
    except Exception as e:
        print("\nERROR: ",e,"\n")
        print("ERROR: The images could not be saved!")

    # saving the graphs
    if graph:
        try:
            for i in range(len(graphData)):
                savename = os.path.join(folder,str(i)+"_graph_"+filename+".png")
                savename = savename.replace("\\", "/")#This line is necessary beacause of exe build issues with cx_freeze
                #generating the graph
                fig, ax = plt.subplots()
                iterations = np.arange(len(graphData[i]))
                ax.plot(iterations, graphData[i])
                ax.set(xlabel='Metric(info.txt)', ylabel='Iteration',
                       title='graph '+str(i))
                ax.grid()
                fig.savefig(savename)
                #plt.show()
            #saving the combined graphs
            print("printing combined Graph")
            savename = os.path.join(folder,str(i)+"_CombinedGraph_"+filename+".png")
            savename = savename.replace("\\", "/")#This line is necessary beacause of exe build issues with cx_freeze
            #generating the graph
            fig, ax = plt.subplots()
            for i in range(len(graphData)):
                ax.plot(np.arange(len(graphData[i])), graphData[i])
            ax.set(xlabel='Metric(info.txt)', ylabel='Iteration',
                   title='Combined Graph ')
            ax.grid()
            fig.savefig(savename)

        except Exception as e:
            print("\nERROR: ",e,"\n")
            print("ERROR: The graphs could not be saved!")


    #saving the Transformations
    try:
        for i in range(len(transformData)):
            savename = os.path.join(folder,str(i)+"_transformation_"+filename+".tfm")
            savename = savename.replace("\\", "/")#This line is necessary beacause of exe build issues with cx_freeze
            sitk.WriteTransform(transformData[i], savename)
    except Exception as e:
        print("\nERROR: ",e,"\n")
        print("ERROR: The transformations could not be saved!")

    # generate a combined Image TODO
    try:
        if isotropic:
            #average
            print("Versuch die Arrays zu kombinieren.(Mittelwert)")
            zDim = len(sitk.GetArrayViewFromImage(output[0]))
            print(zDim)
            mergedVolume = sitk.GetArrayFromImage(output[0])
            for i in range(1,len(output)-1):
                print(i)
                for j in range(zDim-1):
                    print(j)
                    print("mergedVolume[j]",mergedVolume[j].shape)
                    print("output[i][j]",sitk.GetArrayViewFromImage(output[i])[j].shape)
                    mergedVolume[j] = cv2.addWeighted(mergedVolume[j],(i)/(i+1),sitk.GetArrayViewFromImage(output[i])[j],1/(i+1),1)
            savename = os.path.join(folder,"combinedAveraged"+"_"+filename+extOut)
            savename = savename.replace("\\", "/")#This line is necessary beacause of exe build issues with cx_freeze
            sitk.WriteImage(sitk.GetImageFromArray(mergedVolume), savename)
            #keepMax
            print("Versuch die Arrays zu kombinieren.(Maximum)")
            outN = len(output)
            mergedVolume = np.zeros_like(sitk.GetArrayViewFromImage(output[0]))
            for i in range(len(output)):
                mergedVolume = np.maximum(mergedVolume, sitk.GetArrayViewFromImage(output[i]))
            savename = os.path.join(folder,"combinedKeepMax"+"_"+filename+extOut)
            savename = savename.replace("\\", "/")#This line is necessary beacause of exe build issues with cx_freeze
            sitk.WriteImage(sitk.GetImageFromArray(mergedVolume), savename)
    except Exception as e:
        print("\nERROR: ",e,"\n")
        print("!!!Error: combied Image could not be generated.")

    # saving the info text
    try:
        infoText1 += "Info Text Ende."
        savename = os.path.join(folder,'info.txt')
        savename = savename.replace("\\", "/")#This line is necessary beacause of exe build issues with cx_freeze
        with open(savename, 'w') as info:
            info.write(infoText1)
    except Exception as e:
        print("\nERROR: ",e,"\n")
        print("ERROR: The info text could not be saved!")
    # Erzeugen der Ergebnisstabelle
    try:
        def average(x):
            return sum(x)/len(x)
        print("Starten der Ergebnissliste!")
        verbList = []
        slopeList = []
        ergebnissText = "Ergebnisse\n\n"
        ergebnissText += "-----------------------------------------------------\n"
        print("len(graphData)",len(graphData))
        for i in range(len(graphData)):
            ergebnissText += ""+str(i)+"\n"
            #print("ergebnissText",ergebnissText)
            ergStart = graphData[i][0]
            #print("ergStart",str(ergStart))
            ergEnde = graphData[i][-1]
            #print("ergEnde",str(ergEnde))
            ergVerb = ergStart-ergEnde
            #print("ergVerb",str(ergVerb))
            try:
                ergSlope = float(ergVerb)/float(len(graphData[i]))
            except:
                ergSlope = 0
            #print("ergSlope",str(ergSlope))
            verbList.append(ergVerb)
            slopeList.append(ergSlope)
            ergebnissText += "Startwert:    "+str(ergStart)+"\n"
            ergebnissText += "Endwert:      "+str(ergEnde)+"\n"
            ergebnissText += "Steigung(-):     "+str(ergSlope)+"\n"
            ergebnissText += "Iterarionen:  "+str(len(graphData[i]))+"\n"
            ergebnissText += "Verbesserung: "+str(ergVerb)+"\n"

            ergebnissText += "\n"
        ergebnissText += "=====================================================\n"
        ergebnissText += "Durchschnittliche Steigung(-): "+str(average(slopeList))+"\n"
        ergebnissText += "Durchschnittliche Verbesserung: "+str(average(verbList))
        print(ergebnissText)

        savename = os.path.join(folder,'Ergebniss.txt')
        savename = savename.replace("\\", "/")#This line is necessary beacause of exe build issues with cx_freeze
        with open(savename, 'w') as info:
            info.write(ergebnissText)
    except Exception as e:
        print("\nERROR: ",e,"\n")
        print("ERROR: The ergebnissText could not be saved!")

    text = "\nThe data is saved in the folder "+folder+"."
    return text

def turnbackResample(output, degStep):
    '''
    Turning the Volumes back to their original rotation.
    '''
    turnedList = list()
    angles = [-degStep*x for x in range(len(output))]
    for image in output:
        turned = rotation3d(output[i], angles[i], 0, 0, False)
        turnedList.append(turned)

    return turnedList

def registerToFirst(data, gradient, metric, multi, lr, epochs, graph, samplingPercent):
    '''
    Every volume is regsitered to match the first volume.
    '''
    fixedImage = data[0]
    imageListRegistered = list()
    graphList = list()
    transformList = list()
    imageListRegistered.append(fixedImage)
    infoText = ""
    for i in range(1, len(data)):
        movingImage = data[i]
        transform, text, graphImage = registerAlgorithm(fixedImage, movingImage, gradient, metric, multi, lr, epochs, graph, samplingPercent)
        registeredImage = resample(movingImage, transform, False)
        imageListRegistered.append(registeredImage)
        infoText += text+"\n"
        graphList.append(graphImage)
        transformList.append(transform)
    output = imageListRegistered
    return output, infoText, graphList, transformList

def registerToNext(data, gradient, metric, multi, lr, epochs, graph, samplingPercent):
    '''
    Every volume is regsitered to match the previous volume.
    '''

    imageListRegistered = list()
    graphList = list()
    transformList = list()
    infoText = ""
    # First Transformation
    fixedImage = data[0]
    movingImage = data[1]
    transform, text, graphImage = registerAlgorithm(fixedImage, movingImage, gradient, metric, multi, lr, epochs, graph, samplingPercent)
    registeredImage = resample(movingImage, transform, False)
    imageListRegistered.append(fixedImage)
    imageListRegistered.append(registeredImage)
    graphList.append(graphImage)
    transformList.append(transform)
    for i in range(2, len(data)):
        fixedImage = imageListRegistered[i-1]
        movingImage = data[i]
        transform, text, graphImage = registerAlgorithm(fixedImage, movingImage, gradient, metric, multi, lr, epochs, graph, samplingPercent)
        registeredImage = resample(movingImage, transform, False)
        imageListRegistered.append(registeredImage)
        infoText += text+"\n"
        graphList.append(graphImage)
        transformList.append(transform)
    output = imageListRegistered
    return output, infoText, graphList, transformList

def registerAlgorithm(fixed_image, moving_image, gradient, metric, multi, lr, epochs, graph, samplingPercent):
    initial_transform = sitk.CenteredTransformInitializer(fixed_image,
                                                      moving_image,
                                                      sitk.Euler3DTransform(),
                                                      sitk.CenteredTransformInitializerFilter.GEOMETRY)

    registration_method = sitk.ImageRegistrationMethod()

    # Similarity metric settings.
    if metric == "MSE":
        registration_method.SetMetricAsMeanSquares()
    elif metric == "MI":
        print("Mutual Information")
        registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetMetricSamplingPercentage(samplingPercent/100)

    registration_method.SetInterpolator(sitk.sitkLinear)

    # Optimizer settings.
    if gradient == "GD":
        print("Gradient Descent")
        print("epochs: ",epochs)
        registration_method.SetOptimizerAsGradientDescent(learningRate=lr, numberOfIterations=epochs, convergenceMinimumValue=1e-6, convergenceWindowSize=10)
    elif gradient == "GDLS":
        print("Gradient Descent with Line Search")
        print("epochs: ",epochs)
        registration_method.SetOptimizerAsGradientDescentLineSearch(learningRate=lr, numberOfIterations=epochs, convergenceMinimumValue=1e-6, convergenceWindowSize=10)
    registration_method.SetOptimizerScalesFromPhysicalShift()

    # Setup for the multi-resolution framework.
    if multi:
        registration_method.SetShrinkFactorsPerLevel(shrinkFactors = [4,2,1])
        registration_method.SetSmoothingSigmasPerLevel(smoothingSigmas=[2,1,0])
        registration_method.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()

    # Don't optimize in-place, we would possibly like to run this cell multiple times.
    registration_method.SetInitialTransform(initial_transform, inPlace=False)

    # Connect all of the observers so that we can perform plotting during registration.
    plot=list()
    if graph:
        registration_method.AddCommand(sitk.sitkIterationEvent, lambda: plot.append(registration_method.GetMetricValue()))

    final_transform = registration_method.Execute(fixed_image, moving_image)

    # Always check the reason optimization terminated.
    print(final_transform.GetParameters())
    text = '\nFinal metric value: {0}'.format(registration_method.GetMetricValue())
    text += '\nOptimizer\'s stopping condition, {0}'.format(registration_method.GetOptimizerStopConditionDescription())
    text += "\n----------------------------------------------------"
    text += "\nTransformation Name:"
    text += str(final_transform.GetName())
    text += "\nCNumber of Parmeters:"
    text += str(final_transform.GetNumberOfFixedParameters())
    text += str(final_transform.GetNumberOfParameters())
    text += "\nParameters:"
    text += str(final_transform.GetParameters())
    text += "\n----------------------------------------------------"

    return final_transform, text, plot

def loadData(path, extIn, dims, isotropic, degStep):
    srcDir = os.path.abspath(path)
    imageList = list()
    for root, directories, filenames in os.walk(path):
        filenames.sort()
        i=0
        angles = [degStep*x for x in range(len(filenames))]
        for filename in filenames:
            # Check for file extension
            if not filename.lower().endswith(extIn):
                continue
            image = processLoad(root, filename, angles[i], dims, isotropic)
            imageList.append(image)
            i+=1
    return imageList

def processLoad(root, fileName, angle, dims, isotropic):
    # Opening the image
    print ("Open image file", fileName)
    image = tifffile.imread(os.path.join(root, fileName))
    # Converting to SITK
    if len(image.shape)==4:
        image = image[:,:,:,0]
    image = sitk.GetImageFromArray(image.astype("float32"))#to make int a float type
    print(image.GetSize())
    image.SetSpacing(dims)
    print(image.GetPixelIDTypeAsString())
    # Initial Transformation
    image = rotation3d(image, angle, 0, 0, isotropic)
    return image

def resample(image, transform, isotropic):
    """
    source:https://stackoverflow.com/questions/56171643/
    simpleitk-rotation-of-volumetric-data-e-g-mri
    This function resamples (updates) an image using a specified transform
    :param image: The sitk image we are trying to transform
    :param transform: An sitk transform (ex. resizing, rotation, etc.
    :return: The transformed sitk image
    """
    if isotropic:
        lenght = np.max(image.GetSize())
        minDim = np.min(image.GetSpacing())
        #print("minDim", minDim)
        dims = [minDim, minDim, minDim]
        #zLenght = int(np.min(image.GetSize())*np.max(image.GetSpacing())/np.min(image.GetSpacing()))
        #print("zLenght", zLenght)
        reference_image = sitk.GetImageFromArray(np.zeros((lenght,lenght,lenght)).astype("float32"))
        reference_image.SetSpacing(dims)
        #print("Dims: ",dims)
        #TODO transform, die in die mitte verschiebt
    else:
        reference_image = image
    interpolator = sitk.sitkLinear#sitkBSpline
    default_value = 0
    #TODO Prefiltering
    return sitk.Resample(image, reference_image, transform,
                 interpolator, default_value)

def get_center(img):
    """
    source:https://stackoverflow.com/questions/56171643/
    simpleitk-rotation-of-volumetric-data-e-g-mri
    This function returns the physical center point of a 3d sitk image
    :param img: The sitk image we are trying to find the center of
    :return: The physical center point of the image
    """
    width, height, depth = img.GetSize()
    return img.TransformIndexToPhysicalPoint((int(np.ceil(width/2)),
                                          int(np.ceil(height/2)),
                                          int(np.ceil(depth/2))))

def rotation3d(image, theta_x, theta_y, theta_z, isotropic):
    """
    source:https://stackoverflow.com/questions/56171643/
    simpleitk-rotation-of-volumetric-data-e-g-mri
    This function rotates an image across each of the x, y, z axes
    by theta_x, theta_y, and theta_z degrees
    respectively
    :param image: An sitk MRI image
    :param theta_x: The amount of degrees the user wants the image
    rotated around the x axis
    :param theta_y: The amount of degrees the user wants the image
    rotated around the y axis
    :param theta_z: The amount of degrees the user wants the image
    rotated around the z axis
    :param show: Boolean, whether or not the user wants to see the
    result of the rotation
    :return: The rotated image
    """
    theta_x = np.deg2rad(theta_x)
    theta_y = np.deg2rad(theta_y)
    theta_z = np.deg2rad(theta_z)
    euler_transform = sitk.Euler3DTransform(get_center(image),
                                        theta_x, theta_y, theta_z, (0, 0, 0))
    image_center = get_center(image)
    euler_transform.SetCenter(image_center)
    euler_transform.SetRotation(theta_x, theta_y, theta_z)
    #print(euler_transform)
    resampled_image = resample(image, euler_transform, isotropic)

    return resampled_image
