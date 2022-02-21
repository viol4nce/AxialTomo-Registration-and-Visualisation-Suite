from tifffile import tifffile
import numpy as np
import open3d as o3d
import os

import Code.Helper as Helper

#Generate Lists
def pointcloudRender(volume, noiseThreshold, zScale, caged):
    print("inside Solo Pointcloud")
    winkel = np.pi/4
    angles = [winkel*x for x in range(0,8) ]
    if len(volume.shape) == 4:
        volume = volume[:,:,:,0]
    if caged==True:
        volume = Helper.cage(volume)

    pointcloud, pointcloudColor = Helper.generatePointcloud(volume, 1.1*zScale, 1.1, 1.1, noiseThreshold, (1,1,1))

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pointcloud)
    pcd.colors = o3d.utility.Vector3dVector(pointcloudColor)


    Helper.custom_draw_geometry_load_option(pcd)
