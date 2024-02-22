import bpy

class Scene():

    def __init__(self, clean=True, alpha=0.5, clip_start=0.1,
                 clip_end=1000, fps=36, frame_start=0, frame_end=100):

        if clean:

            if bpy.context.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")

            # Delete all objects in the scene
            if bpy.data.objects:
                bpy.ops.object.select_all(action="SELECT")
                bpy.ops.object.delete()

            # delete all materials in the scene
            if bpy.data.materials:
                for material in bpy.data.materials:
                    bpy.data.materials.remove(material)

            # delete all lights
            if bpy.data.lights:
                for light in bpy.data.lights:
                    bpy.data.lights.remove(light)
            
            # delete all cameras
            if bpy.data.cameras:
                for camera in bpy.data.cameras:
                    bpy.data.cameras.remove(camera)

            # delete all images
            if bpy.data.images:
                for image in bpy.data.images:
                    bpy.data.images.remove(image)

            # delete all meshes
            if bpy.data.meshes:
                for mesh in bpy.data.meshes:
                    bpy.data.meshes.remove(mesh)

            view_layers = bpy.context.scene.view_layers
            for vl in view_layers:
                if vl.name != 'ViewLayer':
                    bpy.context.scene.view_layers.remove(vl)


            # Remove all handlers
            bpy.app.handlers.frame_change_pre.clear()

            # Delete all collections except the default "Collection" and "Master Collection"
            collections_to_delete = [
                c
                for c in bpy.data.collections
                if c.name not in ["Collection", "Master Collection"]
            ]
            for collection in collections_to_delete:
                bpy.data.collections.remove(collection)

            # Remove all worlds
            for world in bpy.data.worlds:
                bpy.data.worlds.remove(world)

            # Ensure all changes to data are reflected in the scene
            bpy.context.view_layer.update()

            # Set cursor location to the origin
            bpy.context.scene.cursor.location = (0, 0, 0)

        if alpha is not None:
            world = bpy.data.worlds.new("New World")
            bpy.context.scene.world = world
            world.use_nodes = True

            bg_node = world.node_tree.nodes["Background"]
            bg_node.inputs[0].default_value = (alpha, alpha, alpha, 1)

        bpy.context.scene.frame_start = frame_start
        bpy.context.scene.frame_set(frame_start)
        bpy.context.scene.frame_end = frame_end

        bpy.context.scene.render.fps = fps

        for area in bpy.context.screen.areas:
            # Check if the area is a 3D View
            if area.type == 'VIEW_3D':
                # Access the 3D View space
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        # Set the start and end clipping planes
                        space.clip_start = clip_start
                        space.clip_end = clip_end


    def render(self, resolution=(720, 720)):

        bpy.context.scene.render.resolution_x = resolution[0]
        bpy.context.scene.render.resolution_y = resolution[1]

        bpy.context.scene.render.resolution_percentage = 100

    def set_eevee(self, bloom=True, 
                  viewport_samples=32,
                  render_samples=64,
                  bl_threshold=0.8,
                  bl_radius=6.5,
                  bl_intensity=0.05,
                  bl_clamp=10,
                  volumetric_tile_size=2,
                  volumetric_samples=64,
                  volumetric_clip_start=0.1,
                  volumetric_clip_end=1000):

        bpy.context.scene.render.engine = "BLENDER_EEVEE"
        bpy.context.scene.eevee.use_bloom = bloom

        bpy.context.scene.eevee.taa_render_samples = render_samples
        bpy.context.scene.eevee.taa_samples = viewport_samples

        bpy.context.scene.eevee.bloom_threshold = bl_threshold
        bpy.context.scene.eevee.bloom_radius = bl_radius
        bpy.context.scene.eevee.bloom_intensity = bl_intensity
        bpy.context.scene.eevee.bloom_clamp = bl_clamp

        bpy.context.scene.eevee.volumetric_tile_size = f'{volumetric_tile_size}'
        bpy.context.scene.eevee.volumetric_samples = volumetric_samples
        bpy.context.scene.eevee.volumetric_start = volumetric_clip_start
        bpy.context.scene.eevee.volumetric_end = volumetric_clip_end

        
    def set_cycles(self,
                   viewport_samples=32,
                   render_samples=64,
                   time_limit=15,
                   gpu=True,
                   denoise=False,
                   ligh_paths='eco',
                   tiles=(256, 256),
                   adaptative_threshold=0.01,
                   volume_step=100,
                   volume_max_steps=2):

        bpy.context.scene.render.engine = "CYCLES"

        cycles = bpy.context.scene.cycles

        cycles.preview_samples = viewport_samples
        cycles.samples = render_samples
        cycles.time_limit = time_limit

        prefs = bpy.context.preferences
        cycles_prefs = prefs.addons['cycles'].preferences

        if gpu==True:
            # Set the compute device type
            cycles_prefs.compute_device_type = 'CUDA'  # or 'OPTIX' for RTX cards, 'OPENCL' for AMD

            # Enable GPU device(s), assuming you have at least one GPU
            for device in cycles_prefs.devices:
                if device.type == 'CUDA' or device.type == 'OPTIX':
                    device.use = True  # Enable the device for rendering

            cycles.device = 'GPU'

            cycles.tile_x = tiles[0]
            cycles.tile_y = tiles[1]

        

        if denoise:
            cycles.use_denoising = True
            cycles.denoiser = 'OPENIMAGEDENOISE'
        else:
            cycles.use_denoising = False

        if ligh_paths == 'eco':

            cycles.max_bounces = 4  
            cycles.diffuse_bounces = 0  
            cycles.glossy_bounces = 0  
            cycles.transmission_bounces = 0  
            cycles.volume_bounces = 0  
            cycles.transparent_max_bounces = 0  
            cycles.transparent_min_bounces = 0  

            cycles.caustics_reflective = False
            cycles.caustics_refractive = False

        if adaptative_threshold is not None:
            cycles.use_adaptive_sampling = True
            cycles.adaptive_threshold = adaptative_threshold


        cycles.volume_step_size = volume_step  # Adjust based on desired detail and render time
        cycles.volume_max_steps = volume_max_steps  # Increase or decrease based on complexity
        # viewport step size
        cycles.volume_step_rate = 100

        return
    

def set_camera(position, 
               look_at=(0, 0, 0), 
               camera_type='PERSP',
               focal_length=50, 
               ortho_scale=6.0,
               depth_of_field=None, 
               fstop=2.8, 
               name='Camera'):

    # if camera exists with that name, delete it
    if name in bpy.data.objects:
        cam_to_delete = bpy.data.objects[name]
        cam_data_name = cam_to_delete.data.name  # Store the camera data name before deletion

        # Delete the camera object
        bpy.data.objects.remove(cam_to_delete, do_unlink=True)

        # Delete the camera data if it exists
        if cam_data_name in bpy.data.cameras:
            bpy.data.cameras.remove(bpy.data.cameras[cam_data_name], do_unlink=True)


    bpy.ops.object.camera_add(align="VIEW", location=position, rotation=(0, 0, 0))
    camera = bpy.context.active_object
    camera.name = name
    camera.data.name = name
    
    # Set camera type and lens properties
    if camera_type == 'PERSP':
        camera.data.type = 'PERSP'
        camera.data.lens = focal_length
    elif camera_type == 'ORTHO':
        camera.data.type = 'ORTHO'
        camera.data.ortho_scale = ortho_scale
    elif camera_type == 'PANO':
        camera.data.type = 'PANO'
        camera.data.lens = focal_length
    else:
        print("Invalid camera type. Use 'PERSP', 'ORTHO', or 'PANO'.")

    # Depth of Field settings
    if depth_of_field is not None:
        camera.data.dof.use_dof = True
        camera.data.dof.focus_distance = depth_of_field
        camera.data.dof.aperture_fstop = fstop

    # Add empty and set it as the camera's target
    #bpy.ops.object.empty_add(type="PLAIN_AXES", align="WORLD", location=look_at)
    empty_origin = add_empty_origin(look_at, name=f'{name}_target')
    add_track_to_constraint(camera, empty_origin, name=f'{name}_constraint')
    return camera



def add_track_to_constraint(obj, target, name='constraint'):
    # Check if a constraint with the specified name already exists
    for existing_constraint in obj.constraints:
        if existing_constraint.name == name:
            # Remove the existing constraint if found
            obj.constraints.remove(existing_constraint)
            break

    # Create a new constraint
    constraint = obj.constraints.new(type="TRACK_TO")
    constraint.name = name
    constraint.target = target
    constraint.track_axis = "TRACK_NEGATIVE_Z"
    constraint.up_axis = "UP_Y"

    return constraint

def add_empty_origin(look_at, name='EmptyOrigin'):
    # Check if an empty object with the specified name already exists
    if name in bpy.data.objects:
        empty_to_delete = bpy.data.objects[name]
        bpy.data.objects.remove(empty_to_delete, do_unlink=True)

    # Create a new empty object
    bpy.ops.object.empty_add(type="PLAIN_AXES", align="WORLD", location=look_at)
    empty_origin = bpy.context.active_object
    empty_origin.name = name

    return empty_origin