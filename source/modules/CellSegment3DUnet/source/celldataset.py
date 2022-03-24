import glob
import os
import numpy as np
# from matplotlib import pyplot as plt
import SimpleITK as sitk
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, utils
from skimage import segmentation
from skimage.transform import resize
import time
from skimage.filters import gaussian
import random


class cell_training(Dataset):
    def __init__(self, data_path):
        self.data_path = data_path
        self.data_names = []
        self.seg_names = []
        subdir = next(os.walk(self.data_path))[1]
        # print(sorted(subdir))
        length = 0
        for name in subdir:
            dirname = os.path.join(self.data_path, name)
            data_file = "processed_tiffs"
            # filename = "segmentation_tiffs"
            data_file = os.path.join(dirname, data_file)
            # dirname = os.path.join(dirname,filename)
            # print data_file
            # _,_,files = next(os.walk(dirname))
            _, _, data_files = next(os.walk(data_file))
            '''for each in files:
                full_name = os.path.join(dirname,each)
                self.seg_names.append(full_name)
            '''
            for each_data in data_files:
                if "acylYFP" in each_data:
                    data_fullname = os.path.join(data_file, each_data)
                    self.data_names.append(data_fullname)

    def __len__(self):
        return len(self.data_names)

    def __getitem__(self, inx):
        img = sitk.ReadImage(self.data_names[inx])
        img = sitk.GetArrayFromImage(img)
        _, filename = os.path.split(self.data_names[inx])
        filename = os.path.splitext(filename)[0]
        plant = filename.split('_')[1]
        seg_path = os.path.join(self.data_path, plant)
        seg_path = os.path.join(seg_path, "segmentation_tiffs")
        _, _, files = next(os.walk(seg_path))
        for seg_file in files:
            if filename == seg_file[0:len(filename)]:
                seg = sitk.ReadImage(os.path.join(seg_path, seg_file))
                # print 'filename',self.data_names[inx]
                # print 'segmentation_file',seg_path+'/'+seg_file
                seg = sitk.GetArrayFromImage(seg)
                break
        # plt.imshow(seg[0,:,:])
        # plt.show()
        z, x, y = img.shape
        if x != 512 or y != 512:
            img = resize(img, (z, 512, 512))
            seg = resize(seg, (z, 512, 512))
        start_z = random.randint(0, z - 16)
        img = img[start_z:start_z + 16, :, :]
        img = img.astype('float32') / (2 ** 8 - 1)
        # img = resize(img,(135,512,512))
        seg = segmentation.find_boundaries(seg, connectivity=1, mode='thick')
        # plt.imshow(seg[0,:,:],cmap='gray')
        # plt.show()
        seg = seg[start_z:start_z + 16, :, :]
        # seg = resize(seg,(135,512,512))
        seg = seg.astype('float32')
        sample = {}
        sample['data'] = img[None, ...]
        sample['seg'] = seg[None, ...]
        return sample


class cell_training_cells(Dataset):
    def __init__(self, data_path):
        self.data_path = data_path
        self.data_names = []
        self.seg_names = []
        subdir = next(os.walk(self.data_path))[1]
        # print(sorted(subdir))
        length = 0
        for name in subdir:
            dirname = os.path.join(self.data_path, name)
            data_file = "processed_tiffs"
            # filename = "segmentation_tiffs"
            data_file = os.path.join(dirname, data_file)
            # dirname = os.path.join(dirname,filename)
            # print data_file
            # _,_,files = next(os.walk(dirname))
            _, _, data_files = next(os.walk(data_file))
            '''for each in files:
                full_name = os.path.join(dirname,each)
                self.seg_names.append(full_name)
            '''
            for each_data in data_files:
                if "acylYFP" in each_data:
                    data_fullname = os.path.join(data_file, each_data)
                    self.data_names.append(data_fullname)

    def __len__(self):
        return len(self.data_names)

    def __getitem__(self, inx):
        img = sitk.ReadImage(self.data_names[inx])
        img = sitk.GetArrayFromImage(img)
        _, filename = os.path.split(self.data_names[inx])
        filename = os.path.splitext(filename)[0]
        plant = filename.split('_')[1]
        seg_path = os.path.join(self.data_path, plant)
        seg_path = os.path.join(seg_path, "segmentation_tiffs")
        _, _, files = next(os.walk(seg_path))
        for seg_file in files:
            if filename == seg_file[0:len(filename)]:
                seg = sitk.ReadImage(os.path.join(seg_path, seg_file))
                # print 'filename',self.data_names[inx]
                # print 'segmentation_file',seg_path+'/'+seg_file
                seg = sitk.GetArrayFromImage(seg)
                break
        # plt.imshow(seg[0,:,:])
        # plt.show()
        z, x, y = img.shape
        if x != 512 or y != 512:
            img = resize(img, (z, 512, 512))
            seg = resize(seg, (z, 512, 512))
        start_z = random.randint(0, z - 16)
        img = img[start_z:start_z + 16, :, :]
        img = img.astype('float32') / (2 ** 8 - 1)
        # img = resize(img,(135,512,512))
        seg = segmentation.find_boundaries(seg, connectivity=1, mode='thick')
        # plt.imshow(seg[0,:,:],cmap='gray')
        # plt.show()
        seg = seg[start_z:start_z + 16, :, :]
        # seg = resize(seg,(135,512,512))
        seg = seg.astype('float32')
        sample = {}
        sample['data'] = img[None, ...]
        sample['seg'] = seg[None, ...]
        return sample


class cell_training_patch(Dataset):
    def __init__(self, data_path):
        self.data_path = data_path
        # self.images = np.load(self.data_path+'/inputs.npy')
        # self.ground_truths = np.load(self.data_path+'/ground_truth.npy')

    def __len__(self):
        return (len(os.listdir(self.data_path + '/gts')))

    def __getitem__(self, inx):
        img = np.load(self.data_path + '/inputs/' + "%.5i" % inx + '.npy')
        seg = np.load(self.data_path + '/gts/' + "%.5i" % inx + '.npy')
        # seg = self.ground_truths[inx:inx+1]
        img = img.transpose(1, 2, 0)
        img = img.astype('float32') / (2 ** 8 - 1)
        seg = seg.astype('float32')
        img = img[None, ...]
        sample = {}
        sample['data'] = img
        sample['seg'] = seg
        return sample


class cell_testing(Dataset):
    def __init__(self, data_path):
        self.data_path = data_path
        self.files = os.listdir(self.data_path)

    def __len__(self):
        return len(self.files)

    def __getitem__(self, inx):
        full_path = os.path.join(self.data_path, self.files[inx])
        img = sitk.ReadImage(full_path)
        img = sitk.GetArrayFromImage(img)
        img = img.astype('float32')
        img = img / (2 ** 8 - 1)
        img = gaussian(img)
        # plt.imshow(img[0,:,:],cmap='gray')
        # plt.show()
        z, x, y = img.shape
        int_z = int(np.power(2, np.ceil(np.log2(z))))
        image_inter = resize(img, (5 * z, 512, 512))
        expo = np.ceil(np.log2(5 * z))
        z_dim = 2 ** expo
        z_dim = int(z_dim)
        image_new = np.zeros((z_dim, x, y))
        image_new[0:int(5 * z)] = image_inter
        # img = image_new.astype('float32')
        # plt.imshow(seg[0,:,:],cmap='gray')
        # plt.show()
        sample = {}
        sample['seg'] = []
        sample['data'] = image_new[None, ...]
        sample['name'] = self.files[inx]
        sample['image_size'] = [z, x, y]
        return sample


class cell_testing_inter(Dataset):
    def __init__(self, data_path):
        self.data_path = data_path
        self.files = os.listdir(self.data_path)

    def __len__(self):
        return len(self.files)

    def __getitem__(self, inx):
        full_path = os.path.join(self.data_path, self.files[inx])
        img = sitk.ReadImage(full_path)
        img = sitk.GetArrayFromImage(img)
        img = img.astype('float32')
        img = img / (2 ** 8 - 1)
        img = gaussian(img)
        # plt.imshow(img[0,:,:],cmap='gray')
        # plt.show()
        z, x, y = img.shape
        z = z / 5
        int_z = int(np.power(2, np.ceil(np.log2(5 * z))))
        # image_inter = resize(img,(5*z,512,512))
        image_new = np.zeros((int_z, x, y))
        image_new[0:int(5 * z)] = img
        # img = image_new.astype('float32')
        # plt.imshow(seg[0,:,:],cmap='gray')
        # plt.show()
        sample = {}
        sample['seg'] = []
        sample['data'] = image_new[None, ...]
        sample['name'] = self.files[inx]
        sample['image_size'] = [z, x, y]
        return sample


class IndexTracker(object):
    def __init__(self, ax, X):
        self.ax = ax
        ax.set_title('use scroll wheel to navigate images')
        self.X = X
        self.slices, rows, cols = X.shape
        self.ind = self.slices // 2
        self.im = ax.imshow(self.X[self.ind, :, :], cmap='gray')
        self.update()

    def onscroll(self, event):
        print("%s %s" % (event.button, event.step))
        if event.button == 'up':
            self.ind = (self.ind + 1) % self.slices
        else:
            self.ind = (self.ind - 1) % self.slices
        self.update()

    def update(self):
        self.im.set_data(self.X[self.ind, :, :])
        self.ax.set_ylabel('slice %s' % self.ind)
        self.im.axes.figure.canvas.draw()


class IndexTracker2(object):
    def __init__(self, ax, X, Y):
        self.ax = ax
        ax.set_title('use scroll wheel to navigate images')
        self.X = X
        self.slices, rows, cols = X.shape
        self.ind = self.slices // 2
        self.im = ax.imshow(self.X[self.ind, :, :], cmap='gray')
        # self.cmap2 = cmap2
        self.Y = Y
        self.im2 = ax.imshow(self.Y[self.ind, :, :], cmap='gray', alpha=0.3)
        self.update()

    def onscroll(self, event):
        print("%s %s" % (event.button, event.step))
        if event.button == 'up':
            self.ind = (self.ind + 1) % self.slices
        else:
            self.ind = (self.ind - 1) % self.slices
        self.update()

    def update(self):
        self.im.set_data(self.X[self.ind, :, :])
        self.ax.set_ylabel('slice %s' % self.ind)
        self.im.axes.figure.canvas.draw()


class IndexTracker2plot(object):
    def __init__(self, ax1, ax2, X, Y):
        self.ax1 = ax1
        self.ax2 = ax2
        ax1.set_title('use scroll wheel to navigate images')
        ax2.set_title('use scroll wheel to navigate images')
        self.X = X
        self.Y = Y
        self.slices, rows, cols = X.shape
        self.ind = self.slices // 2
        self.im1 = ax1.imshow(self.X[self.ind, :, :], cmap='gray')
        self.im2 = ax2.imshow(self.Y[self.ind, :, :], cmap='gray')
        self.update()

    def onscroll(self, event):
        print("%s %s" % (event.button, event.step))
        if event.button == 'up':
            self.ind = (self.ind + 1) % self.slices
        else:
            self.ind = (self.ind - 1) % self.slices
        self.update()

    def update(self):
        self.im1.set_data(self.X[self.ind, :, :])
        self.im2.set_data(self.Y[self.ind, :, :])
        self.ax1.set_ylabel('slice %s' % self.ind)
        self.ax2.set_ylabel('slice %s' % self.ind)
        self.im1.axes.figure.canvas.draw()
        self.im2.axes.figure.canvas.draw()


'''
if __name__=='__main__':
    cell = cell_training('/source/data/PNAS/')
    cell_test = cell_testing('/source/data/celldata/')
    img1 = cell.__getitem__(0)['data']
    img2 = cell_test.__getitem__(0)['data']
    img1 = img1[0]
    img2 = img2[0]
    fig,ax = plt.subplots(1,1)
    tracker = IndexTracker(ax,img1)
    fig.canvas.mpl_connect('scroll_event', tracker.onscroll)
    fig2,ax2 = plt.subplots(1,1)
    tracker2 = IndexTracker(ax2,img2)
    fig2.canvas.mpl_connect('scroll_event', tracker2.onscroll)
    plt.show()'''
