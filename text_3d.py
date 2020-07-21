# -*- coding: utf-8 -*-
# @Author: meng-zha
# @Date:   2020-07-21 10:34:56
# @Last Modified by:   meng-zha
# @Last Modified time: 2020-07-21 10:42:33

#https://github.com/intel-isl/Open3D/issues/2#issuecomment-610683341
from PIL import Image, ImageFont, ImageDraw
import open3d as o3d
import numpy as np


def text_3d(text, pos, font="/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", font_size=50):
    """
    Generate a 3D text point cloud used for visualization.
    :param text: content of the text
    :param pos: 3D xyz position of the text upper left corner
    :param direction: 3D normalized direction of where the text faces
    :param degree: in plane rotation of text
    :param font: Name of the font - change it according to your system
    :param font_size: size of the font
    :return: o3d.geoemtry.PointCloud object
    """
    font_obj = ImageFont.truetype(font, font_size)
    font_dim = font_obj.getsize(text)

    img = Image.new('RGB', font_dim, color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), text, font=font_obj, fill=(0, 0, 0))
    img = np.asarray(img)
    img_mask = img[:, :, 0] < 128
    indices = np.indices([*img.shape[0:2], 1])[:, img_mask, 0].reshape(3, -1).T
    indices[:,0]*=-1

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(indices[:,[1,2,0]] / 100.0)
    pcd.paint_uniform_color([1,0,0])

    pcd.translate(pos,relative=False)

    return pcd
