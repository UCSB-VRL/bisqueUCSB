import os
import re
import torch
from train import initialize_generator
from utils import generate_random_tensors, generate_binvox_file
from argparser import Argparser

@torch.no_grad()
def get_mean_style(generator):
    mean_style = None

    mean_style = torch.randn(1, 512)

    return mean_style


@torch.no_grad()
def sample(generator, step, mean_style, args, n_sample=1):
    voxel = generator(
        torch.randn(n_sample, 512),
        step=step,
        alpha=1,
        mean_style=mean_style,
        style_weight=0.7,
    )

    voxel = voxel.view(n_sample, args.cube_len, args.cube_len, args.cube_len)    
    return voxel

def main():
    """
    Entrypoint for test
    Creates 6 binvox files using a specified generator
    """
    test_no = 0
    
    args = Argparser().args
    test_path  = args.test_path
    base_name = os.path.basename(test_path)
    model_name = os.path.splitext(base_name)[0]
    regex = re.compile(r'\d+')
    epoch_no = int(regex.findall(model_name)[0])
    network_name = os.path.split(test_path)[0]
    g_model = initialize_generator(args).eval()
    if not os.path.exists(f'./{network_name}'):
        os.mkdir(f'./{network_name}')

    
    device = 'cuda'
 
    step = 4
     
    mean_style = get_mean_style(g_model) 
    
    voxels = sample(g_model, step, mean_style, args,  n_sample=8)
 
    #voxels = voxels.detach().cpu()
   
    for voxel in voxels:

        generate_binvox_file(voxel, f'{network_name}/{test_no}_{epoch_no}_epochs', args.cube_len)
 
        test_no += 1
    


if __name__ == '__main__':
    main()
