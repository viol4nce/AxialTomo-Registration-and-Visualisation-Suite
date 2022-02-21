from tifffile import tifffile
import numpy as np
import open3d as o3d
import os

import Code.Helper as Helper

def loadVolume(path, caged):
    image = tifffile.imread(path)
    if len(image.shape) == 4:
        image = image[:,:,:,1]
        if caged==True:
            image = Helper.cage(image)
    return image

# Open Vizualiser Window
def custom_draw_geometry_load_option(pcList):
    option = o3d.visualization.RenderOption()
    option.show_coordinate_frame=True
    option.background_color=[0.0, 0.0, 0.0]
    option.save_to_json("renderoption.json")
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    for pc in pcList:
        vis.add_geometry(pc)
    vis.get_render_option().load_from_json("renderoption.json")
    vis.run()
    vis.destroy_window()

#Generate Lists
def pointcloudRender(path, extIn, noiseThreshold, zScale, caged, corrected, degStep):
    # Parameter
    color1 = [1.0, 1.0, 1.0] # Weiß
    color2 = [1.0, 0.0, 0.0] # Rot
    color3 = [0.0, 1.0, 0.0] # Grün
    color4 = [0.0, 0.0, 1.0] # Blau
    color5 = [0.0, 1.0, 1.0] # Cyan
    color6 = [1.0, 0.0, 1.0] # Magenta
    color7 = [1.0, 1.0, 0.0] # Gelb
    color8 = [1.0, 0.5, 0.0] # Orange oder so

    filenames = Helper.generateFilenames(path, extIn)

    colors = [color1,color2,color3,color4,color5,color6,color7,color8]
    pointclouds = []
    winkel = np.deg2rad(degStep)#np.pi/4
    angles = [winkel*x for x in range(0,len(filenames)) ]
    for i in range(0,len(colors)):

        volume = loadVolume(filenames[i], caged)

        pointcloud, pointcloudColor = Helper.generatePointcloud(volume, zScale*1.1, 1.1, 1.1, noiseThreshold, colors[i%len(colors)])

        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(pointcloud)
        pcd.colors = o3d.utility.Vector3dVector(pointcloudColor)
        if corrected == False:
            R = pcd.get_rotation_matrix_from_xyz((0, 0, angles[i]))
            pcd.rotate(R)

        pointclouds.append(pcd)


    custom_draw_geometry_load_option(pointclouds)
