#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************
#
#     ex.py
#
# ************************************************************

from ursina import *
from ursina.shaders import *

app = Ursina()

# sun = DirectionalLight()
# sun .look_at(Vec3(1, 1, 1))

cube = Entity(
    model="../assets/cube.fbx",
    scale=1,
    collider="box",
    color=color.white,
    double_sided=True,
    shader=colored_lights_shader,
)



def spin():
    cube.animate(
        "rotation_y", cube.rotation_y + 360, duration=2, curve=curve.in_out_expo
    )


cube.on_click = spin
EditorCamera()  # add camera controls for orbiting and moving the camera

app.run()
