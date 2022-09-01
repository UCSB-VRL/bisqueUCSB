import os
from sklearn.model_selection import train_test_split

import torch
from torchvision import datasets, transforms
#import cv2
import numpy as np
from torch.utils.data import Dataset
#from mypath import Path
from PIL import Image

class SequentialDataset(Dataset):
    

    def __init__(self, stack_dir, transform, clip_len=16,clip_jump=1, preprocess=False,deeper_layer=False):
        print('Incomplete implementation. Works only for one stack in the plant.')
        
        self.stack_dir = stack_dir
        folder = os.path.join(self.stack_dir)
        self.clip_len = clip_len
        self.clip_jump = clip_jump
        self.transform = transform

        # The following three parameters are chosen as described in the paper section 4.1
        self.resize_height = 256
        self.resize_width = 256
        self.crop_size = 256
     
        #assert (self.clip_len % self.clip_jump) == 0
        #assert self.clip_len > self.clip_jump 
        
        self.stack_names, labels = [], []
        self.frame_names = []
        self.stack_len = []
        for label in sorted(os.listdir(folder)):
            for fname in sorted(os.listdir(os.path.join(folder, label))):
                self.stack_names.append(os.path.join(folder, label, fname))
                stack_fnames = sorted(os.listdir(self.stack_names[-1]))
                stack_len = len(stack_fnames)
                assert (stack_len - self.clip_len*self.clip_jump) >= 0
                for f_idx in range(stack_len): # - self.clip_len*self.clip_jump):
                     self.frame_names.append(os.path.join(self.stack_names[-1],stack_fnames[f_idx]))
                labels.append(label)

        assert len(labels) == len(self.stack_names)
        print('Number of stack in {} : {:d}'.format(folder, len(self.stack_names)))
         
        # Prepare a mapping between the label names (strings) and indices (ints)
        self.label2index = {label: index for index, label in enumerate(sorted(set(labels)))}

        # Convert the list of label names into an array of label indices
        self.label_array = np.array([self.label2index[label] for label in labels], dtype=int)
        
    def __len__(self):
        return len(self.frame_names) - self.clip_len*self.clip_jump

    def __getitem__(self, index):
        # Loading and preprocessing.
        #print(index)
        
        buffer_list = self.load_frames(self.frame_names)
        buffer = np.empty((self.clip_len, 3, self.resize_height, self.resize_width), np.dtype('float32'))
        buffer_list = self.get_nFrames(buffer_list, self.clip_len, self.clip_jump, index)
        
        for i in range(len(buffer_list)):
            buffer[i] = self.transform(buffer_list[i])

        return torch.from_numpy(buffer[0]), torch.from_numpy(buffer)

    def load_frames(self, frames):
        buffer_list = []
        for i, frame_name in enumerate(frames):
            frame = Image.open(frame_name).convert('RGB')
            buffer_list.append(frame)
      
        return buffer_list

  
    def get_nFrames(self, buffer_list, clip_len, clip_jump=1,init_time_idx=-1):
        # randomly select time index for temporal jittering
        if init_time_idx > 0 and init_time_idx < len(buffer_list):
            time_index = init_time_idx
        elif init_time_idx > len(buffer_list):
            assert init_time_idx > (len(buffer_list) - clip_jump*clip_len)
        else:
            #import pdb; pdb.set_trace()
            time_index = np.random.randint(len(buffer_list) - clip_jump*clip_len + 1)
        
        buffer_list = buffer_list[time_index:time_index + clip_jump*clip_len:clip_jump]

        return buffer_list





if __name__ == "__main__":
    DATA_DIR = '/home/agupt013/projects/reconstruction/vq-vae-2-pytorch/data/'
    from torch.utils.data import DataLoader
    train_data = SequentialDataset(DATA_DIR, split='train', clip_len=3, preprocess=False)
    train_loader = DataLoader(train_data, batch_size=10, shuffle=True, num_workers=4)

    for i, sample in enumerate(train_loader):
        inputs = sample[0]
        labels = sample[1]
        print(inputs)
        print(labels.size())

        if i == 1:
            break
