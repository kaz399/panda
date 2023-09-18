#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     main.py
#
# ************************************************************

import asyncio
import argparse
import fileinput
import numpy as np
import math
import pprint
import os
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from logging import (
    DEBUG,
    INFO,
    NOTSET,
    WARNING,
    Formatter,
    Handler,
    NullHandler,
    StreamHandler,
    getLogger,
)
from scipy.spatial.transform import Rotation

from direct.showbase.ShowBase import ShowBase
from direct.task.TaskManagerGlobal import taskMgr
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
from panda3d.core import LQuaternionf

from toio.simple import SimpleCube
from toio.cube import ButtonState, IndicatorParam, PostureAngleEulerData, PostureAngleQuaternionsData, ToioCoreCube, Button, Color, Sensor, PostureAngleDetectionType, PostureAngleDetectionCondition

logger = getLogger(__name__)
if __name__ == "__main__":
    default_log_level = DEBUG
    handler: Handler = StreamHandler()
    handler.setLevel(default_log_level)
    formatter = Formatter("%(asctime)s %(levelname)7s %(message)s")
    handler.setFormatter(formatter)
    logger.setLevel(default_log_level)
else:
    default_log_level = NOTSET
    handler = NullHandler()
logger.addHandler(handler)

@dataclass
class CubeEuler:
    x: float = 0
    y: float = 0
    z: float = 0

    def np_array_xyz(self):
        return np.array([self.x, self.y, self.z])

    def np_array_zyx(self):
        return np.array([self.z, self.y, self.x])

@dataclass
class CubeQuaternion:
    W: float = 0
    X: float = 0
    Y: float = 0
    Z: float = 0
    quat: LQuaternionf = LQuaternionf(r=0, i=0, j=0, k=0)

    def np_array_XYZW(self):
        return np.array([self.X, self.Y, self.Z, self.W])


class CubeButtonState(Enum):
    Pressed = 0
    Released = 1
    Ack = 2

@dataclass
class CubeState:
    button_pressed: CubeButtonState = CubeButtonState.Released
    euler_update: bool = False
    euler: CubeEuler = field(default_factory=CubeEuler)
    emulated_euler: CubeEuler = field(default_factory=CubeEuler)
    quaternion_update: bool = False
    quaternion: CubeQuaternion = field(default_factory=CubeQuaternion)
    emulated_quaternion: CubeQuaternion = field(default_factory=CubeQuaternion)


CUBE_STATE: CubeState = CubeState()


def button_handler(payload: bytearray) -> None:
    button_info = Button.is_my_data(payload)
    if button_info is not None:
        logger.info("notification: " + pprint.pformat(str(button_info)))
        print("notification: " + pprint.pformat(str(button_info)))
        if button_info.state == ButtonState.PRESSED:
            CUBE_STATE.button_pressed = CubeButtonState.Pressed
        elif button_info.state == ButtonState.RELEASED:
            CUBE_STATE.button_pressed = CubeButtonState.Released


def sensor_handler(payload: bytearray) -> None:
    sensor_info = Sensor.is_my_data(payload)
    if isinstance(sensor_info, PostureAngleEulerData):
        CUBE_STATE.euler_update = True
        CUBE_STATE.euler.x = sensor_info.roll
        CUBE_STATE.euler.y = sensor_info.pitch
        CUBE_STATE.euler.z = sensor_info.yaw
        order = "xyz"
        rot = Rotation.from_euler(order, CUBE_STATE.euler.np_array_xyz(), degrees=True)
        logger.info(f"Euler: x:{sensor_info.roll}, y:{sensor_info.pitch}, z:{sensor_info.yaw}")
        quat = rot.as_quat(canonical=True)
        logger.info(f"Emulated Quaternion: x:{quat[0]:4F}, y:{quat[1]:4F}, z:{quat[2]:4F}, w:{quat[3]:4F}")
        (x, y, z) = rot.as_euler(order, degrees=True)
        logger.info(f"Emulated Euler {order}: x:{x:.4f}, y:{y:.4f}, z:{z:.4f}")
    elif isinstance(sensor_info, PostureAngleQuaternionsData):
        CUBE_STATE.quaternion_update = True
        CUBE_STATE.quaternion.W = sensor_info.w / 10000.0
        CUBE_STATE.quaternion.X = sensor_info.x / 10000.0
        CUBE_STATE.quaternion.Y = sensor_info.y / 10000.0
        CUBE_STATE.quaternion.Z = sensor_info.z / 10000.0
        CUBE_STATE.quaternion.quat = LQuaternionf(
            CUBE_STATE.quaternion.W,
            CUBE_STATE.quaternion.X,
            CUBE_STATE.quaternion.Y,
            CUBE_STATE.quaternion.Z,
        )

        rot = Rotation.from_quat(CUBE_STATE.quaternion.np_array_XYZW())
        logger.info(f"Quaternion: x:{CUBE_STATE.quaternion.X}, y:{CUBE_STATE.quaternion.Y}, z:{CUBE_STATE.quaternion.Z}, w:{CUBE_STATE.quaternion.W}")
        # order = "XYZ"
        # (x, y, z) = rot.as_euler(order, degrees=True)
        # logger.info(f"Emulated Euler {order}: x:{x:.4f}, y:{y:.4f}, z:{z:.4f}")
        # order = "XZY"
        # (x, z, y) = rot.as_euler(order, degrees=True)
        # logger.info(f"Emulated Euler {order}: x:{x:.4f}, y:{y:.4f}, z:{z:.4f}")
        # order = "YXZ"
        # (y, x, z) = rot.as_euler(order, degrees=True)
        # logger.info(f"Emulated Euler {order}: x:{x:.4f}, y:{y:.4f}, z:{z:.4f}")
        # order = "YZX"
        # (y, z, x) = rot.as_euler(order, degrees=True)
        # logger.info(f"Emulated Euler {order}: x:{x:.4f}, y:{y:.4f}, z:{z:.4f}")
        # order = "ZYX"
        # (z, y, x) = rot.as_euler(order, degrees=True)
        # logger.info(f"Emulated Euler {order}: x:{x:.4f}, y:{y:.4f}, z:{z:.4f}")
        # order = "ZXY"
        # (z, x, y) = rot.as_euler(order, degrees=True)
        # logger.info(f"Emulated Euler {order}: x:{x:.4f}, y:{y:.4f}, z:{z:.4f}")

        order = "xyz"
        (x, y, z) = rot.as_euler(order, degrees=True)
        logger.info(f"Emulated Euler {order}: x:{x:.4f}, y:{y:.4f}, z:{z:.4f}")
        # order = "xzy"
        # (x, z, y) = rot.as_euler(order, degrees=True)
        # logger.info(f"Emulated Euler {order}: x:{x:.4f}, y:{y:.4f}, z:{z:.4f}")
        # order = "yxz"
        # (y, x, z) = rot.as_euler(order, degrees=True)
        # logger.info(f"Emulated Euler {order}: x:{x:.4f}, y:{y:.4f}, z:{z:.4f}")
        # order = "yzx"
        # (y, z, x) = rot.as_euler(order, degrees=True)
        # logger.info(f"Emulated Euler {order}: x:{x:.4f}, y:{y:.4f}, z:{z:.4f}")
        # order = "zyx"
        # (z, y, x) = rot.as_euler(order, degrees=True)
        # logger.info(f"Emulated Euler {order}: x:{x:.4f}, y:{y:.4f}, z:{z:.4f}")
        # order = "zxy"
        # (z, x, y) = rot.as_euler(order, degrees=True)
        # logger.info(f"Emulated Euler {order}: x:{x:.4f}, y:{y:.4f}, z:{z:.4f}")


class MyApp(ShowBase):
    def __init__(self, opt: argparse.Namespace):
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
        # obj_path = "../assets/cube_noconv.fbx"
        obj_path = Filename.fromOsSpecific(os.path.abspath(opt.model))
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

        #self.obj_model.setScale(2.5)
        self.obj_model.setScale(opt.scale)

        self.obj_coordinate.setScale(5)

        self.taskMgr.add(self.update, "cube update")

    def update(self, task):
        if CUBE_STATE.quaternion_update:
            self.obj_model.setQuat(CUBE_STATE.quaternion.quat)
            CUBE_STATE.quaternion_update = False
        elif CUBE_STATE.euler_update:
            # XYZ rotation (Z -> Y -> X)
            self.obj_model.setHpr(0, 0, 0)
            self.obj_model.setH(self.obj_model, CUBE_STATE.euler.z)
            self.obj_model.setR(self.obj_model, CUBE_STATE.euler.y) # Roll = axis Y (in panda3d)
            self.obj_model.setP(self.obj_model, CUBE_STATE.euler.x) # Pitch = axis X (in panda3d)
            CUBE_STATE.euler_update = False
        return task.cont



def options(argv):
    op = argparse.ArgumentParser()
    op.add_argument("--dry-run", action="store_true", help="do not perform actions")
    op.add_argument("-v", "--verbose", action="store_true", help="verbose mode")
    op.add_argument("-q", "--quiet", action="store_true", help="quiet mode")
    op.add_argument("-m", "--model", action="store", help="3D model", type=str, default="../assets/cube_noconv.fbx")
    op.add_argument("-s", "--scale", action="store", help="scale", type=float, default=1.0)
    op.add_argument("argv", nargs="*", help="args")
    opt = op.parse_args(argv[1:])
    # set logging level
    if opt.quiet:
        loglevel = WARNING
    elif opt.verbose:
        loglevel = DEBUG
    else:
        loglevel = INFO
    handler.setLevel(loglevel)
    logger.setLevel(loglevel)
    return opt


async def main(argv):
    opt = options(argv)
    angle_type = PostureAngleDetectionType.Quaternions

    async with await SimpleCube.search() as cube:
        print("** CONNECTED")
        await cube.api.button.register_notification_handler(button_handler)
        await cube.api.sensor.register_notification_handler(sensor_handler)
        await cube.api.configuration.set_posture_angle_detection(
            PostureAngleDetectionType.Euler, 100, PostureAngleDetectionCondition.ChangeDetection
        )
        await cube.api.indicator.turn_on(
            IndicatorParam(
                duration_ms=0,
                color=Color(r=0, g=128, b=32),
            )
        )
        my_app = MyApp(opt)
        try:
            while True:
                await asyncio.sleep(0)

                if CUBE_STATE.button_pressed == CubeButtonState.Pressed:
                    CUBE_STATE.button_pressed = CubeButtonState.Ack

                    await cube.api.configuration.set_posture_angle_detection(
                        angle_type, 100, PostureAngleDetectionCondition.ChangeDetection
                    )
                    if angle_type == PostureAngleDetectionType.Quaternions:
                        angle_type = PostureAngleDetectionType.Euler
                    else:
                        angle_type = PostureAngleDetectionType.Quaternions
                taskMgr.step()
        finally:
            await cube.api.sensor.unregister_notification_handler(sensor_handler)
            await cube.api.button.unregister_notification_handler(button_handler)
            await cube.api.indicator.turn_off_all()
            print("** DISCONNECTING")
    print("** DISCONNECTED")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main(sys.argv)))

