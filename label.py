# -*- coding: utf-8 -*-
# @Author: meng-zha
# @Date:   2020-07-18 10:52:15
# @Last Modified by:   meng-zha
# @Last Modified time: 2020-07-21 11:36:15

import os
import numpy as np
from PIL import Image, ImageFont, ImageDraw
import open3d as o3d

from text_3d import text_3d

class Annotator(object):
    def __init__(self, data_path, det_path, label_path):
        super().__init__()
        self.data_path = data_path
        self.det_path = det_path
        self.label_path = label_path
        self.geometries = []
        self.text = []
        self.track = []

        self.image_idxes = [int(f[3:].split(".")[0]) for f in os.listdir(data_path)]
        self.image_idxes.sort()
        self.pos = 2

        self.vis = o3d.visualization.VisualizerWithKeyCallback()
        # keycallback
        # https://www.glfw.org/docs/latest/group__keys.html

        # load pcd
        self.vis.register_key_callback(ord("."), self.move_next)
        self.vis.register_key_callback(ord(","), self.move_prev)
        # load label
        self.vis.register_key_callback(ord("D"), self.load_det)
        self.vis.register_key_callback(ord("L"), self.load_label)
        # save label
        self.vis.register_key_callback(ord("S"), self.save_label)
        # translate
        self.vis.register_key_callback(265, self.trans_forward)
        self.vis.register_key_callback(264, self.trans_back)
        self.vis.register_key_callback(262, self.trans_left)
        self.vis.register_key_callback(263, self.trans_right)
        # rotate
        self.vis.register_key_callback(ord("R"), self.rotate)
        # scale
        self.vis.register_key_callback(ord('1'),self.expand_x)
        self.vis.register_key_callback(ord('2'),self.shrink_x)
        self.vis.register_key_callback(ord('3'),self.expand_y)
        self.vis.register_key_callback(ord('4'),self.shrink_y)
        self.vis.register_key_callback(ord('5'),self.expand_z)
        self.vis.register_key_callback(ord('6'),self.shrink_z)
        # delete
        self.vis.register_key_callback(ord('X'),self.delete_box)
        # add
        self.vis.register_key_callback(ord('N'),self.new_box)
        # switch the acitivate
        self.vis.register_key_callback(257,self.switch_activate) 
        # change track id
        self.vis.register_key_callback(266,self.id_up)   #pageup
        self.vis.register_key_callback(267,self.id_down)   #pagedown

        self.activate = 0 # which bounding box is activated
        self.vis.create_window()
        self.setup(self.image_idxes[self.pos], True)
        self.vis.run()

    def setup(self,idx, init=False):
        # self.geometries = []
        # self.track=[]
        # self.text=[]
        pcd_path = os.path.join(self.data_path,f"PC_{idx}.pcd")
        pcd = o3d.io.read_point_cloud(pcd_path)
        if len(self.geometries):
            self.geometries[0] = pcd
        else:
            self.geometries.append(pcd)
        if init:
            self.render(True)
        else:
            self.render()

    def render(self,init=False):
        self.vis.clear_geometries()
        if init:
            for geo in self.geometries:
                self.vis.add_geometry(geo)
        else:
            for geo in self.geometries:
                self.vis.add_geometry(geo, reset_bounding_box=False)
            for text in self.text:
                self.vis.add_geometry(text,reset_bounding_box=False)

        self.vis.poll_events()
        self.vis.update_renderer()

    # key call_back
    def move_next(self,vis):
        if self.pos<len(self.image_idxes)-1:
            self.pos += 1
            self.setup(self.image_idxes[self.pos])
            print(self.image_idxes[self.pos])

    def move_prev(self,vis):
        if self.pos>0:
            self.pos -= 1
            self.setup(self.image_idxes[self.pos])
            print(self.image_idxes[self.pos])

    def load_det(self,vis):
        for i in range(1,len(self.geometries)):
            del self.geometries[1]
            del self.track[0]
            del self.text[0]

        bbox_path = os.path.join(self.det_path,f"PC_{self.image_idxes[self.pos]}.txt")
        dets = np.loadtxt(bbox_path)

        bbox = [] 
        for i in range(dets.shape[0]):
            ori_box = o3d.geometry.OrientedBoundingBox(dets[i][4:7],o3d.geometry.get_rotation_matrix_from_zxy([dets[i][7],0,0]),dets[i][1:4])
            ori_box.color = [1,0,0]
            self.geometries.append(ori_box)
            self.track.append(int(dets[i][8]))
            self.text.append(text_3d(f'{int(dets[i][8])}',dets[i][4:7]+[0,0,dets[i][3]*0.6]))

        self.render()

    def load_label(self,vis):
        for i in range(1,len(self.geometries)):
            del self.geometries[1]
            del self.track[0]
            del self.text[0]

        bbox_path = os.path.join(self.label_path,f"PC_{self.image_idxes[self.pos]}.txt")
        dets = np.loadtxt(bbox_path)

        bbox = [] 
        for i in range(dets.shape[0]):
            ori_box = o3d.geometry.OrientedBoundingBox(dets[i][4:7],o3d.geometry.get_rotation_matrix_from_zxy([dets[i][7],0,0]),dets[i][1:4])
            ori_box.color = [1,0,0]
            self.geometries.append(ori_box)
            self.track.append(int(dets[i][8]))
            self.text.append(text_3d(f'{int(dets[i][8])}',dets[i][4:7]+[0,0,dets[i][3]*0.6]))

        self.render()

    def save_label(self,vis):
        label = np.zeros((len(self.track),9))
        for i in range(len(self.track)):
            label[i][0] = 1
            label[i][8] = self.track[i]
            label[i][1:4] = self.geometries[i+1].extent
            label[i][4:7] = self.geometries[i+1].center
            R = self.geometries[i+1].R
            label[i][7] = np.math.atan2(R[1,0],R[0,0])
        np.savetxt(os.path.join(self.label_path,f"PC_{self.image_idxes[self.pos]}.txt"),label)       
        print(f"save the label of PC_{self.image_idxes[self.pos]} successfully!")

    def trans_forward(self,vis):
        if self.activate > 0:
            self.geometries[self.activate].translate([0.1,0,0])
            self.text[self.activate-1].translate([0.1,0,0])
            self.render()

    def trans_back(self,vis):
        if self.activate > 0:
            self.geometries[self.activate].translate([-0.1,0,0])
            self.text[self.activate-1].translate([-0.1,0,0])
            self.render()

    def trans_right(self,vis):
        if self.activate > 0:
            self.geometries[self.activate].translate([0,-0.1,0])
            self.text[self.activate-1].translate([0,-0.1,0])
            self.render()

    def trans_left(self,vis):
        if self.activate > 0:
            self.geometries[self.activate].translate([0,0.1,0])
            self.text[self.activate-1].translate([0,0.1,0])
            self.render()

    def rotate(self,vis):
        if self.activate > 0:
            # open3d 0.9.0 need not the center coord
            # center = self.geometries[self.activate].get_center()
            self.geometries[self.activate].rotate(o3d.geometry.get_rotation_matrix_from_zxy([0.2,0,0]),True)
            self.render()

    def expand_x(self,vis):
        scale = 1.1
        if self.activate > 0:
            ori_box = self.geometries[self.activate]
            ori_box = o3d.geometry.OrientedBoundingBox(ori_box.center,ori_box.R,ori_box.extent*[scale,1,1])
            ori_box.color = [1,0,0]
            self.geometries[self.activate]=ori_box
            self.render()

    def expand_y(self,vis):
        scale = 1.1
        if self.activate > 0:
            ori_box = self.geometries[self.activate]
            ori_box = o3d.geometry.OrientedBoundingBox(ori_box.center,ori_box.R,ori_box.extent*[1,scale,1])
            ori_box.color = [1,0,0]
            self.geometries[self.activate]=ori_box
            self.render()

    def shrink_x(self,vis):
        scale = 0.9
        if self.activate > 0:
            ori_box = self.geometries[self.activate]
            ori_box = o3d.geometry.OrientedBoundingBox(ori_box.center,ori_box.R,ori_box.extent*[scale,1,1])
            ori_box.color = [1,0,0]
            self.geometries[self.activate]=ori_box
            self.render()

    def shrink_y(self,vis):
        scale = 0.9
        if self.activate > 0:
            ori_box = self.geometries[self.activate]
            ori_box = o3d.geometry.OrientedBoundingBox(ori_box.center,ori_box.R,ori_box.extent*[1,scale,1])
            ori_box.color = [1,0,0]
            self.geometries[self.activate]=ori_box
            self.render()

    def expand_z(self,vis):
        scale = 1.1
        if self.activate > 0:
            ori_box = self.geometries[self.activate]
            ori_box = o3d.geometry.OrientedBoundingBox(ori_box.center*[1,1,scale],ori_box.R,ori_box.extent*[1,1,scale])
            ori_box.color = [1,0,0]
            self.geometries[self.activate]=ori_box
            self.text[self.activate-1].translate([0,0,ori_box.extent[2]*(scale-1)])
            self.render()

    def shrink_z(self,vis):
        scale = 0.9
        if self.activate > 0:
            ori_box = self.geometries[self.activate]
            ori_box = o3d.geometry.OrientedBoundingBox(ori_box.center*[1,1,scale],ori_box.R,ori_box.extent*[1,1,scale])
            ori_box.color = [1,0,0]
            self.geometries[self.activate]=ori_box
            self.text[self.activate-1].translate([0,0,ori_box.extent[2]*(scale-1)])
            self.render()

    def delete_box(self,vis):
        if self.activate > 0:
            self.vis.remove_geometry(self.geometries[self.activate],reset_bounding_box=False)
            self.vis.remove_geometry(self.text[self.activate-1],reset_bounding_box=False)
            del self.geometries[self.activate]
            del self.track[self.activate-1]
            del self.text[self.activate-1]
            self.activate-=1
            self.vis.poll_events()
            self.vis.update_renderer()

    def new_box(self,vis):
        ori_box = o3d.geometry.OrientedBoundingBox([0,0,0.9],np.eye(3),[0.6,0.8,1.8])
        self.geometries.append(ori_box)
        self.track.append(len(self.track))
        self.text.append(text_3d(f"{self.track[-1]}",[0,0,1.8]))
        self.activate = len(self.geometries)-1
        self.render()

    def switch_activate(self,vis):
        if self.activate:
            self.text[self.activate-1].paint_uniform_color([1,0,0])
        self.activate+=1
        self.activate%=len(self.geometries)
        if self.activate:
            self.text[self.activate-1].paint_uniform_color([0,0,1])
            self.render()

    def id_up(self,vis):
        if self.activate:
            self.track[self.activate-1]+=1
            act = self.geometries[self.activate]
            self.text[self.activate-1] = text_3d(f'{self.track[self.activate-1]}',act.center+[0,0,act.extent[2]*0.6])
            self.text[self.activate-1].paint_uniform_color([0,0,1])
            self.render()

    def id_down(self,vis):
        if self.activate:
            self.track[self.activate-1]-=1
            if self.track[self.activate-1] <= 0:
                print("The track id should be natural number.")
            act = self.geometries[self.activate]
            self.text[self.activate-1] = text_3d(f'{self.track[self.activate-1]}',act.center+[0,0,act.extent[2]*0.6])
            self.text[self.activate-1].paint_uniform_color([0,0,1])
            self.render()

def main():
    print("Hello, World!")
    anno = Annotator("/media/meng-zha/58b26bdb-c733-4c63-b7d9-4d845394a721/BeiCao_20191211/mid100_pcd/Lidar",
                      "/media/meng-zha/58b26bdb-c733-4c63-b7d9-4d845394a721/BeiCao_20191211/mid100_pcd/BeiCao_Label","annotations")


if __name__ == "__main__":
    main()