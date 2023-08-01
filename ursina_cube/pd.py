#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     pd.py
#
# ************************************************************

from direct.showbase.ShowBase import ShowBase
from panda3d.core import Filename
from panda3d.core import Point3
from panda3d.core import Vec3
from panda3d.core import AmbientLight
from panda3d.core import DirectionalLight
from panda3d.core import PandaNode
from panda3d.core import NodePath
from panda3d.core import PointLight
from panda3d.core import Material
from panda3d.core import LColor

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.disableMouse()

        # カメラの位置と方向を設定
        self.camera.setPos(50, -10, -10)
        self.camera.lookAt(Point3(0, 0, 0))
        self.camera.setR(180)

        # ライト
        light = DirectionalLight("light")
        light.setColor(LColor(1, 1, 1, 1))  # 白色の光
        light.setShadowCaster(True)  # 影を生成するように設定
        light.setDirection((-100, 100, 20))  # 光の方向を設定
        light_np = self.render.attachNewNode(light)
        self.render.setLight(light_np)

        # モデルを読み込む
        obj_path = "../assets/cube_noconv.fbx"
        self.obj_model = self.loader.loadModel(obj_path)
        self.obj_model.reparentTo(self.render)
        print(self.obj_model.getQuat())

        coordinate_path = "../assets/coordinate2.fbx"
        self.obj_coordinate = self.loader.loadModel(coordinate_path)
        self.obj_coordinate.reparentTo(self.render)

        # モデルの位置とスケールを調整
        self.obj_model.setPos(0, 0, 0)
        #self.obj_model.setH(self.obj_model, -90)
        #self.obj_model.setHpr(0, 0, 0)
        self.obj_model.setScale(1)

        self.obj_coordinate.setScale(5)


my_app = MyApp()
my_app.run()
