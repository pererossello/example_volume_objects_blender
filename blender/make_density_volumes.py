import os
import sys
import importlib

import bpy

# Necessary for pointing to the local_blutils.py file
cwd = os.getcwd()
sys.path.append(cwd+r'/blender/')
import local_blutils as lblut
from init_scene import Scene, set_camera
importlib.reload(lblut)

Scene = Scene(clean=True, alpha=0)
Scene.render(resolution=(720, 720))
Scene.set_cycles(viewport_samples=64,
                 render_samples=64,
                 volume_step=10, 
                 volume_max_steps=64)

path_vdb = cwd + '/blender/vdb_files/density.vdb'
resolution = 100
scale = 10
volume_obj_1 = lblut.make_volume(path_vdb, 
                               resolution=resolution, 
                               scale=scale,
                               center_location=(2.5,0,0),
                               name='density_1')

volume_obj_2 = lblut.make_volume(path_vdb, 
                               resolution=resolution, 
                               scale=scale,
                               center_location=(-2.5,0,0),
                               name='density_2')

volume_material_1 = lblut.volume_material(color_1=(1,0,0, 1),
                                          color_2=(1,1,1,1),
                                          multiply=1,
                                          divide=0.9)
volume_obj_1.data.materials.append(volume_material_1)

volume_material_2 = lblut.volume_material(color_1=(0,1,0, 1),
                                          color_2=(1,1,1,1),
                                          multiply=1,
                                          divide=0.9)
volume_obj_2.data.materials.append(volume_material_2)


# set camera
camera = set_camera((0,30,0), 
                    camera_type='PERSP', 
                    focal_length=60,
                    look_at=(0,0,0)
                    )