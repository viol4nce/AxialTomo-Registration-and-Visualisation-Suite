import numpy as np
import open3d as o3d
import os

#open folder
def generateFilenames(folder, extIn):
    fList = []
    print("folder: ", folder)
    print("extIn Helper: ",extIn)
    for root, directories, filenames in os.walk(folder):
        filenames.sort()
        for filename in filenames:
            # Check for file extension
            if not filename.lower().endswith(extIn):
                continue
            fList.append(os.path.join(root,filename))
            print(filename)
    return fList

# Draw an outline around the volumes
def cage(volume):
    max = np.max(volume)
    z,y,x = volume.shape
    volume[0,0,:] = max
    volume[:,0,0] = max
    volume[0,:,0] = max
    volume[z-1,y-1,:] = max
    volume[:,y-1,x-1] = max
    volume[z-1,:,x-1] = max
    volume[0,y-1,:] = max
    volume[:,0,x-1] = max
    volume[0,:,x-1] = max
    volume[z-1,0,:] = max
    volume[:,y-1,0] = max
    volume[z-1,:,0] = max
    return volume

# Generate pointcloud
def generatePointcloud(image, z_scale, y_scale, x_scale, thresh, color):
    pointcloudColor = list()
    # threshold
    points = np.asarray(np.where(image>thresh))


    #pointcloud
    indicesZ = points[0]
    indicesY = points[1]
    indicesX = points[2]
    pointcloud = np.zeros((points.shape[1], 3))
    pointcloud[:, 0] = np.reshape(indicesZ, -1)*z_scale
    pointcloud[:, 1] = np.reshape(indicesY, -1)*y_scale
    pointcloud[:, 2] = np.reshape(indicesX, -1)*x_scale
    pointcloudColor = [color for x in range(pointcloud.shape[0])]
    # print("pointcloud")
    # print(pointcloud.shape)
    # print(pointcloud)
    return pointcloud.tolist(), pointcloudColor

# Open Vizualiser Window
def custom_draw_geometry_load_option(pcd):
    option = o3d.visualization.RenderOption()
    option.show_coordinate_frame=True
    option.background_color=[0.0, 0.0, 0.0]
    option.save_to_json("renderoption.json")
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(pcd)
    vis.get_render_option().load_from_json("renderoption.json")
    vis.run()
    vis.destroy_window()
