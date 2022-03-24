import argparse
import time
import os
import logging
import random
import pickle
import shutil
import SimpleITK as sitk
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
import torch.backends.cudnn as cudnn
cudnn.benchmark = True
from torchvision import transforms,utils
from .model import Modified3DUNet
from .celldataset import cell_training,IndexTracker,IndexTracker2,cell_testing,cell_testing_inter
from .utils import Parser, criterions
#import matplotlib
#import matplotlib.pyplot as plt
from skimage.transform import resize
from .losses import *
from skimage.transform import resize

def readprops(proppath):
    props = dict()
    with open(proppath) as file: # 'model/regression/cfg.txt
        for line in file:
            entry = line.strip().split(':', 1)
            props[entry[0].strip()]=entry[1].strip()
    print(props)
    return props

#parser = argparse.ArgumentParser()
#parser.add_argument('-cfg','--cfg',default = 'cell',type=str)

path = os.path.dirname(__file__)

# parse arguments
#args = parser.parse_args()
#args = Parser(args.cfg, args)
#ckpts = args.getdir()

def saveimage(image,filename):
    data = sitk.GetImageFromArray(image)
    sitk.WriteImage(data,filename)

def main(model_path, cell_hist_datadir, prob_map_datadir):
    props = readprops(os.path.join(model_path,'cfg.txt'))
    # setup environments and seeds
    os.environ['CUDA_VISIBLE_DEVICES'] = props['gpu']

    # setup networks
    #Network = getattr(models, args.net)
    #model = Network(**args.net_params)

    model = Modified3DUNet(in_channels = 1,n_classes = 2, base_n_filter = 16)
    #load_model
    model_file = os.path.join(model_path,'model_last.tar')
    checkpoint = torch.load(model_file,
            map_location = lambda storage, loc: storage)
    model.load_state_dict(checkpoint['state_dict'])
    if torch.cuda.is_available():
        model = model.cuda()

    criterion = getattr(criterions, props['criterion'])
    num_gpus = len(props['gpu'].split(','))
    batch_size = int(props['batch_size']) * num_gpus
    workers    = int(props['workers']) * num_gpus

    # create dataloaders
    #Dataset = getattr(datasets, args.dataset)
    dset = cell_testing_inter(cell_hist_datadir)
    #print dset.__len__()
    test_loader = DataLoader(
            dset, batch_size=batch_size,
            shuffle=True,
            num_workers=0,
            pin_memory = True)
    model.eval()
    torch.set_grad_enabled(False)
    inputs = []
    outputs=[]
    ground_truth = []
    #print test_loader
    for i, sample in enumerate(test_loader):
        input1 = sample['data']
        img_size = sample['image_size']
        #print img_size[0]
        file_name = sample['name']
        file_name = os.path.splitext(file_name[0])[0] # str(file_name[0])
        _,_,z,x,y = input1.shape
        seg = np.zeros((z,x,y))
        for j in range (z//16):
            target = sample['seg']
            #ground_truth.append(target)
            #print file_name[0]
            input_temp = input1[0,0,int(j*16):int((j+1)*16)].float()
            input_temp = input_temp[None,None,...]
            # output_temp = nn.parallel.data_parallel(model, input_temp, output_device=torch.device('cpu'))
            output_temp = model(input_temp)
            output_temp = output_temp.detach().cpu().numpy()
            output_temp = output_temp[0]
            seg_temp = output_temp.argmax(0)
            seg[int(j*16):int((j+1)*16)] = seg_temp
        data = input1.detach().numpy()
        #print data.shape
        data = data[0,0,:,:,:]
        data = (255*data[0:int(5*img_size[0])]).astype('uint8')
        #outputs.append(output)
        #output = output[0]
        #print output.shape
        #seg = output.argmax(0)
        prob_map = (seg[0:int(5*img_size[0])]*255).astype('uint8')
        prob_map = prob_map.astype('float32')
        prob_map = prob_map/255.0
        prob_map = np.multiply(data,prob_map)
        prob_map = resize(prob_map,(prob_map.shape[0]/5,prob_map.shape[1],prob_map.shape[2]))
        prob_map_img = sitk.GetImageFromArray(prob_map.astype('uint8'))
        sitk.WriteImage(prob_map_img, prob_map_datadir+'/'+file_name+'-prob.tif')
    #print len(inputs)
    #print len(outputs)
    #inputs = np.concatenate(inputs)
    #outputs = np.concatenate(outputs)
    #ground_truth = np.concatenate(ground_truth)
    #np.save('/home/tom/Modified-3D-UNet-Pytorch/output/inputs.npy',inputs)
    #np.save('/home/tom/Modified-3D-UNet-Pytorch/output/outputs.npy',outputs)
    #np.save('/home/tom/Modified-3D-UNet-Pytorch/output/ground.npy',ground_truth)


if __name__ == '__main__':
    model_path='model/regression'
    cell_hist_datadir='hist_match/'
    prob_map_datadir='prob_map/'
    main(model_path, cell_hist_datadir, prob_map_datadir)
