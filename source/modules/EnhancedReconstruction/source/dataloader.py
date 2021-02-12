import os
from sklearn.model_selection import train_test_split

import torch
from torchvision import datasets, transforms
#import cv2
import numpy as np
from torch.utils.data import Dataset
#from mypath import Path
from PIL import Image

class VideoDataset(Dataset):
    r"""A Dataset for a folder of videos. Expects the directory structure to be
    directory->[train/val/test]->[class labels]->[videos]. Initializes with a list
    of all file names, along with an array of labels, with label being automatically
    inferred from the respective folder names.

        Args:
            dataset (str): Name of dataset. Defaults to 'ucf101'.
            split (str): Determines which folder of the directory the dataset will read from. Defaults to 'train'.
            clip_len (int): Determines how many frames are there in each clip. Defaults to 16.
            preprocess (bool): Determines whether to preprocess dataset. Default is False.
    """

    def __init__(self, output_dir, transform, split='train', clip_len=16,clip_jump=1, preprocess=False,deeper_layer=False):
        #self.root_dir, self.output_dir = Path.db_dir(dataset)
        self.output_dir = output_dir
        folder = os.path.join(self.output_dir, split)
        self.clip_len = clip_len
        self.clip_jump = clip_jump
        self.split = split
        self.transform = transform
        # The following three parameters are chosen as described in the paper section 4.1
        self.resize_height = 256
        self.resize_width = 256
        self.crop_size = 256
     
        self.fnames, labels = [], []
        for label in sorted(os.listdir(folder)):
            for fname in os.listdir(os.path.join(folder, label)):
                self.fnames.append(os.path.join(folder, label, fname))
                labels.append(label)

        assert len(labels) == len(self.fnames)
        print('Number of {} videos: {:d}'.format(split, len(self.fnames)))

        # Prepare a mapping between the label names (strings) and indices (ints)
        self.label2index = {label: index for index, label in enumerate(sorted(set(labels)))}
        # Convert the list of label names into an array of label indices
        self.label_array = np.array([self.label2index[label] for label in labels], dtype=int)

     
    def __len__(self):
        return 150*len(self.fnames)

    def __getitem__(self, index):
        
        # Loading and preprocessing.
        buffer_list, frame_count = self.load_frames(self.fnames[int(index/150)])
        
        buffer = np.empty((self.clip_len, 3, self.resize_height, self.resize_width), np.dtype('float32'))
        
        buffer_list = self.get_nFrames(buffer_list, self.clip_len,self.clip_jump)
                
        for i in range(len(buffer_list)):
            buffer[i] = self.transform(buffer_list[i])
        return torch.from_numpy(buffer[0]), torch.from_numpy(buffer)    

    def load_frames(self, file_dir):
        frames = sorted([os.path.join(file_dir, img) for img in os.listdir(file_dir)])
        frame_count = len(frames)
        buffer_list = [] 
        for i, frame_name in enumerate(frames):
            frame = Image.open(frame_name).convert('RGB')
            buffer_list.append(frame)           
        return buffer_list, frame_count
    

    def get_nFrames(self, buffer_list, clip_len, clip_jump,init_time_idx=-1):
        # randomly select time index for temporal jittering
        if init_time_idx > 0 and init_time_idx < (len(buffer_list) - clip_jump*clip_len):
            time_index = init_time_idx
        elif init_time_idx > (len(buffer_list) - clip_jump*clip_len):
            assert init_time_idx > (len(buffer_list) - clip_jump*clip_len)
        else:
            time_index = np.random.randint(len(buffer_list) - clip_jump*clip_len)
        
        buffer_list = buffer_list[time_index:time_index + clip_jump*clip_len:clip_jump]

        return buffer_list


if __name__ == "__main__":
    DATA_DIR = '/home/agupt013/projects/reconstruction/vq-vae-2-pytorch/data/'
    from torch.utils.data import DataLoader
    train_data = VideoDataset(DATA_DIR, split='train', clip_len=3, preprocess=False)
    train_loader = DataLoader(train_data, batch_size=10, shuffle=True, num_workers=4)

    for i, sample in enumerate(train_loader):
        inputs = sample[0]
        labels = sample[1]
        print(inputs)
        print(labels.size())

        if i == 1:
            break
