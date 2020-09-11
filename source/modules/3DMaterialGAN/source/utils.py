import os
import torch
from torch.utils import data
import numpy as np
from numpy import asarray, float32
import binvox_rw
import h5py
import time
#from tvtk.api import tvtk, write_data

def get_voxels_from_binvox(path):
    """
    Get voxels as numpy from a binvox file
    """
    voxels = binvox_rw.read_as_3d_array(path).data
    return voxels


def generate_z(args):
    """
    Generate a batch of latent vectors
    """
    if args.z_dis == 'norm1':
        Z1 = torch.Tensor(args.batch_size, args.z_size).normal_(0.0, 0.02)
        Z2 = torch.Tensor(args.batch_size, args.z_size).normal_(0.0, 0.02)
        
    elif args.z_dis == 'norm033':
        Z = torch.Tensor(args.batch_size , args.z_size).normal_(0.0, 0.33)
    elif args.z_dis == 'uni':
        Z = torch.randn(args.batch_size , args.z_size)
    return Z1, Z2

'''
class ShapeNetDataset(data.Dataset):
    """Custom Dataset compatible with torch.utils.data.DataLoader"""

    def __init__(self, root):
        self.data = []
        self.root = root
        listdir = os.listdir(self.root)
        for _, path in enumerate(listdir):
            if path.endswith('.binvox'):
                with open(self.root + path, 'rb') as f:
                    self.data.append(torch.FloatTensor(
                        asarray(get_voxels_from_binvox(f), dtype=float32)))

    def __getitem__(self, index):
        return self.data[index]

    def __len__(self):
        return len(self.data)
'''


# feed data one by one
class grain_dataset(data.Dataset):
    """Custom Dataset compatible with torch.utils.data.DataLoader"""
    #import pdb; pdb.set_trace()
    
    def __init__(self, root):
        self.data_files = os.listdir(root)
        self.root = root
        #self.count = 0
        #self.data = []
    def load_file(self, filename):
        #start_time = time.time()
        #print("Loading Data")

        
        with open(self.root+ filename, 'rb') as f:
            data = torch.FloatTensor(asarray(get_voxels_from_binvox(f), dtype=float32))
        #print("Data is Loaded")
        #end_time = time.time()
        #total_time = end_time - start_time
        #print("time elapsed", total_time) 

        return data
        
     
            
    def __getitem__(self, index):
        #print(self.data_files[index])
        #self.count = self.count +1 
        #print(self.count) 
        file_name = self.data_files[index] 
        return self.load_file(file_name)
   
    def __len__(self):
        return len(self.data_files)

              
      


def generate_binvox_file(voxels, file_path, dimension):
    """
    Generate a binvox file from voxels
    """
    voxels = torch.round(voxels.view(dimension, dimension, dimension))
    voxels[voxels < 0] = 0 
    voxels[voxels > 1] = 1
    arr = voxels.numpy()
    size = len(arr)
    dims = [size, size, size]
    scale = 1.0
    translate = [0.0, 0.0, 0.0]
    np.save(f'{file_path}.npy', arr)
    #grid = tvtk.ImageData(spacing=(1, 1, 1), origin=( 0, 0, 0),
    #                  dimensions=arr.shape)
    #grid.point_data.scalars = arr.ravel(order='F')
    #grid.point_data.scalars.name = 'Test Data'
    #write_data(grid, f'{file_path}.vtk')
    model = binvox_rw.Voxels(arr, dims, translate, scale, 'xyz')
    model.write(f'{file_path}.binvox')


def generate_random_tensors(n, args, testing=False):
    """
    Generate n random latent vectors for testing
    """
    if testing:
        torch.manual_seed(999)
    if args.z_dis == 'norm1':
        return torch.rand(n, args.z_size).normal_(0.0, 1.0)
    elif args.z_dis == 'norm033':
        return torch.rand(n, args.z_size).normal_(0.0, 0.33)
    elif args.z_dis == 'uni':
        return torch.randn(n, args.z_size)
