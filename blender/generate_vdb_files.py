import os
import sys
import importlib

import numpy as np

# Necessary for pointing to the local_blutils.py file
cwd = os.getcwd()
sys.path.append(cwd+r'/blender/')
import local_blutils as lblut
importlib.reload(lblut)

density_npy_path = cwd  + '/data/density.npy'
density_arr = np.load(density_npy_path)

savefold = cwd + '/blender/vdb_files/'
lblut.save_vdb(density_arr, savefold=savefold, filename=f'density')