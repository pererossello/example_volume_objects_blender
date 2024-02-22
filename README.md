# Example code for volumetric rendering in Blender

## Structure

- `code/utils.py`: Utility functions for generating a density cube.
- `code/generate_density.ipynb`: Generate and save a uniform density sphere

- `data/density.npy`: Example 3D numpy array with density values.

- `blender/generate_vdb_files.py`: Generate .vdb files from a numpy array using the pyopenvdb library (to be run within the Blender python environment).
- `blender/vdb_files/density.vdb`: Example of .vdb files generated from numpy array

- `blender/make_density_volumes.py`: Create the volumetric objects in Blender (to be run within the Blender python environment).
- `blender/local_blutils.py`: Functions for generating the .vdb files, making volumetric objects, and materials for these objects. 
- `blender/init_scene.py`: Utility classes and functions to initialize an scene in Blender. Sets the render engine and resolution, cleans objects, sets camera, etc. 


