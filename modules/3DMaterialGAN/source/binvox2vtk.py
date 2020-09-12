import os
import binvox_rw
from tvtk.api import tvtk, write_data
import argparse
import torch
from torch.utils import data
from numpy import asarray, float32

def get_voxels_from_binvox(path):
    """
    Get voxels as numpy from a binvox file
    """
    voxels = binvox_rw.read_as_3d_array(path).data
    return voxels

if __name__ == "__main__":
 
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--file_path', type=str, help='path of file')

    arg_parser.add_argument('--save_path', type=str, help='locationwhere you want to save file', required=False)    
    args =  arg_parser.parse_args()  
    import pdb; pdb.set_trace()
    filepath = args.file_path
    base_name = os.path.basename(filepath)
    filename = os.path.splitext(base_name)[0]
    
    with open(filepath, 'rb') as f:  
      voxels = asarray(get_voxels_from_binvox(f), dtype=float32)
    grid = tvtk.ImageData(spacing=(1, 1, 1), origin=( 0, 0, 0), 
                      dimensions=voxels.shape)
    grid.point_data.scalars = voxels.ravel(order='F')
    grid.point_data.scalars.name = 'Test Data'
    write_data(grid, f'{args.save_path}/{filename}.vtk')
 
