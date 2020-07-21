# Point Cloud Label Tool
This is a annotation tool for the 3D detection and tracking of point cloud based on open3d.

## Requiments
open3d = 0.9.0
pillow
numpy

## Handling Instruction
The key bindings come from [GLFW](https://www.glfw.org/docs/latest/group__keys.html).

* ",/.": move prev frame or next frame
* "D/L": load the initial label from det or manual
* "S": save the label to the label_path
* "ENTER": switch the activated box to edit
* "Up/Down;Left/Right": move the activated box in the x-y plane
* "1/2;3/4;5/6": change the size of the activated box
* "R": rotate the activated box
* "PageUp/PageDown": change the track_id of the activated box
* "X": delete the activated bounding box
* "N": new a bounding box at the origin

## Data Path
Edit the `data_path, det_path, label_path` of yourself.  
The LiDAR data should be the '.pcd' file.  
And the annotations are the ".txt", of which each row is (class,l,w,h,x,y,z,yaw,id).

## To be Mentioned
The code is for open3d 0.9.0, while other version open3d can be used
if you change some specific functions, such as the `open3d.geometry.Geometry.rotate()`
in Line 188.