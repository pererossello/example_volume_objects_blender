import os

import numpy as np
import bpy

# This library should be available in the Blender Python environment
import pyopenvdb as vdb

def save_vdb(density, savefold=None, filename='untitled'):

    density = density / np.nanmax(density)
    grid = vdb.FloatGrid()
    grid.copyFromArray(density.astype(float))

    grid.transform = vdb.createLinearTransform(([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]))
    grid.GridClass = vdb.GridClass.FOG_VOLUME
    grid.name = f'density'

    cwd = os.getcwd()

    if savefold is None:
        savefold = cwd + '/blender/vdb_files/'

    if not os.path.exists(savefold):
        os.makedirs(savefold)

    filepath = savefold + filename + '.vdb'

    vdb.write(filepath, grids=[grid])

    return filepath


def make_volume(filepath, resolution=100, scale=10, center_location=(0, 0, 0), 
                name=None):

    if name == None:
        object_name = filepath.split('/')[-1].split('.')[0]
    else:
        object_name = name

    vdb_name = filepath.split('/')[-1].split('.')[0]

    bpy.ops.object.volume_import(filepath=filepath, files=[])

    vol_obj = bpy.data.objects[vdb_name]

    vol_obj.name = object_name

    shape = [resolution, resolution, resolution]
    print(shape)

    vol_obj.scale = (scale/shape[0], scale/shape[1], scale/shape[2])

    shift_x = shape[0] / 2
    shift_y = shape[1] / 2
    shift_z = shape[2] / 2

    vol_obj.location = (-scale*shift_x/shape[0] + center_location[0],
                        -scale*shift_y/shape[1] + center_location[1],
                        -scale*shift_z/shape[2] + center_location[2])

    return vol_obj


def volume_material(name=None, 
                      color_1=(0.523, 0, 1, 1), 
                      color_2 = (0, 0.75, 1, 1),
                      pos_1=0.118, pos_2=1,
                      multiply=.075, 
                      power=1.3,
                      divide=2.6,
                      minimum=129):

    if name is None:
        name = 'VolumeMaterial'
        # check if there are any already with this name
        if name in bpy.data.materials:
            i = 1
            while name + str(i) in bpy.data.materials:
                i += 1
            name = name + str(i)

    material = bpy.data.materials.new(name="VolumeShader")
    material.use_nodes = True
    nodes = material.node_tree.nodes

    # Clear default nodes
    nodes.clear()

    # Create Volume Info node
    volume_info = nodes.new(type='ShaderNodeVolumeInfo')
    volume_info.location = (-800, 0)

    # Create Math node (set to 'POWER')
    power_node = nodes.new(type='ShaderNodeMath')
    power_node.operation = 'POWER'
    power_node.inputs[1].default_value = power # Threshold value
    power_node.location = (-600, 0)

    # minimum node
    minimum_node = nodes.new(type='ShaderNodeMath')
    minimum_node.operation = 'MINIMUM'
    minimum_node.inputs[1].default_value = minimum
    minimum_node.location = (-400, 0)


    # Create Math node (set to 'MULTIPLY')
    multiply_node = nodes.new(type='ShaderNodeMath')
    multiply_node.operation = 'MULTIPLY'
    multiply_node.inputs[1].default_value = multiply  # Multiply value
    multiply_node.location = (-200, 0)

    # Create Math node (set to 'DIVIDE')
    divide_node = nodes.new(type='ShaderNodeMath')
    divide_node.operation = 'DIVIDE'
    divide_node.inputs[1].default_value = divide  # Divide value
    divide_node.location = (-470, -300)

    # create coloramp node with two colors 
    color_ramp_node = nodes.new(type='ShaderNodeValToRGB')
    color_ramp_node.color_ramp.elements[0].color = (0,0,0,1)  
    color_ramp_node.color_ramp.elements[0].position = 0
    color_ramp_node.color_ramp.elements[1].color = color_1
    color_ramp_node.color_ramp.elements[1].position = pos_1
    # color ramp new element 
    color_ramp_node.color_ramp.elements.new(pos_2)
    color_ramp_node.color_ramp.elements[2].color = color_2

    color_ramp_node.location = (-270, -300)

    # Create Principled Volume node
    principled_volume = nodes.new(type='ShaderNodeVolumePrincipled')
    principled_volume.inputs['Density'].default_value = 0
    principled_volume.location = (0, 0)

    # Create Material Output node
    material_output = nodes.new(type='ShaderNodeOutputMaterial')
    material_output.location = (300, 0)

    # Link nodes together
    links = material.node_tree.links
    links.new(volume_info.outputs['Density'], power_node.inputs[0])
    links.new(power_node.outputs[0], minimum_node.inputs[0])
    links.new(minimum_node.outputs[0], multiply_node.inputs[0])
    links.new(multiply_node.outputs[0], principled_volume.inputs['Emission Strength'])
    links.new(principled_volume.outputs['Volume'], material_output.inputs['Volume'])

    links.new(volume_info.outputs['Density'], divide_node.inputs[0])
    links.new(divide_node.outputs[0], color_ramp_node.inputs['Fac'])
    links.new(color_ramp_node.outputs['Color'], principled_volume.inputs['Emission Color'])

    return material