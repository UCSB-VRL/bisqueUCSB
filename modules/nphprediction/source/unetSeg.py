###############################################################################
##  Vision Research Laboratory and                                           ##
##  Center for Multimodal Big Data Science and Healthcare                    ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2019                                                    ##
##     by the Regents of the University of California                        ##
##                            All rights reserved                            ##
##                                                                           ##
## Redistribution and use in source and binary forms, with or without        ##
## modification, are permitted provided that the following conditions are    ##
## met:                                                                      ##
##                                                                           ##
##     1. Redistributions of source code must retain the above copyright     ##
##        notice, this list of conditions, and the following disclaimer.     ##
##                                                                           ##
##     2. Redistributions in binary form must reproduce the above copyright  ##
##        notice, this list of conditions, and the following disclaimer in   ##
##        the documentation and/or other materials provided with the         ##
##        distribution.                                                      ##
##                                                                           ##
##                                                                           ##
## THIS SOFTWARE IS PROVIDED BY <COPYRIGHT HOLDER> "AS IS" AND ANY           ##
## EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE         ##
## IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR        ##
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> OR           ##
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,     ##
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,       ##
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR        ##
## PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF    ##
## LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING      ##
## NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS        ##
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.              ##
##                                                                           ##
## The views and conclusions contained in the software and documentation     ##
## are those of the authors and should not be interpreted as representing    ##
## official policies, either expressed or implied, of <copyright holder>.    ##
###############################################################################

import numpy as np
import os
import nibabel as nib
import matplotlib.pyplot as plt
import torch.nn as nn
import torch.nn.functional as F
import torch
import nibabel as nib
from skimage.transform import resize
import warnings


def fxn():
	warnings.warn("deprecated", DeprecationWarning)


def unetPredict(BASE, gpu=False):
	'''
	Outputs segmentations based on trained unet model.
	'''
	with warnings.catch_warnings():
		warnings.simplefilter("ignore")
		fxn()

	print('-------- UNet Segmentation --------')
	dtype = torch.FloatTensor
	if gpu:
		dtype = torch.cuda.FloatTensor

	Scan_Folder = os.path.join(BASE, 'Scans')
	scans_all = [s for s in os.listdir(Scan_Folder) if (s.endswith('nii.gz') or s.endswith('nii') and not 'MNI152' in s)]

#[s for s in os.listdir(Scan_Folder) if (s.endswith('nii.gz') and not 'MNI152' in s)]

	N1 = 128
	N  = 256
	batch_size = 1

	def NPH_data_gen():
		N_pred = len(scans_all)
		X = np.empty([batch_size,1,N,N,N1])
		while True:
			inds = range(len(scans_all))
			i=0
			while i <= (N_pred - batch_size):
				for j in range(batch_size):
					scanname = scans_all[inds[i+j]]
					img_nib = nib.load(os.path.join(Scan_Folder,scanname))
					img = img_nib.get_data()
					img_info = (img.shape, img_nib.affine)
					img[np.where(img<-1000)] = -1000
					temp_img = resize(img, output_shape=[N,N,N1], preserve_range=True,mode='constant',order=1,anti_aliasing=True)
					X[j,0] = temp_img
				i+=1
				X -= 100
				X /= 100
				yield scanname, img_info, torch.from_numpy(X).type(dtype)

	data_gen = NPH_data_gen()


	''' Loading unet '''

	import models
	from models import criterions, unet

	unet_model = 'source/unet_ce_hard_per_im_s8841_all'
	ckpt = 'model_last.tar'

	unet = unet.Unet()
	unet.cpu()
	if gpu:
		unet.cuda()


	model_file = os.path.join(unet_model, ckpt)
	if gpu:
		device = 'cuda'
	else:
		device = 'cpu'
	checkpoint = torch.load(model_file, map_location=torch.device(device))
	unet.load_state_dict(checkpoint['state_dict'])

	'''Unet Definition'''
	def normalization(planes, norm='gn'):
		if norm == 'bn':
			m = nn.BatchNorm3d(planes)
		elif norm == 'gn':
			m = nn.GroupNorm(4, planes)
		elif norm == 'in':
			m = nn.InstanceNorm3d(planes)
		else:
			raise ValueError('normalization type {} is not supported'.format(norm))
		return m


	class ConvD(nn.Module):
		def __init__(self, inplanes, planes, dropout=0.0, norm='gn', first=False):
			super(ConvD, self).__init__()

			self.first = first
			self.maxpool = nn.MaxPool3d(2, 2)

			self.dropout = dropout
			self.relu = nn.ReLU(inplace=True)

			self.conv1 = nn.Conv3d(inplanes, planes, 3, 1, 1, bias=False)
			self.bn1 = normalization(planes, norm)

			self.conv2 = nn.Conv3d(planes, planes, 3, 1, 1, bias=False)
			self.bn2 = normalization(planes, norm)

			self.conv3 = nn.Conv3d(planes, planes, 3, 1, 1, bias=False)
			self.bn3 = normalization(planes, norm)

		def forward(self, x):
			if not self.first:
				x = self.maxpool(x)
			x = self.bn1(self.conv1(x))
			y = self.relu(self.bn2(self.conv2(x)))
			if self.dropout > 0:
				y = F.dropout3d(y, self.dropout)
			y = self.bn3(self.conv3(x))
			return self.relu(x + y)


	class ConvU(nn.Module):
		def __init__(self, planes, norm='gn', first=False):
			super(ConvU, self).__init__()

			self.first = first

			if not self.first:
				self.conv1 = nn.Conv3d(2*planes, planes, 3, 1, 1, bias=False)
				self.bn1 = normalization(planes, norm)

			self.conv2 = nn.Conv3d(planes, planes//2, 1, 1, 0, bias=False)
			self.bn2 = normalization(planes//2, norm)

			self.conv3 = nn.Conv3d(planes, planes, 3, 1, 1, bias=False)
			self.bn3 = normalization(planes, norm)

			self.relu = nn.ReLU(inplace=True)

		def forward(self, x, prev):
			# final output is the localization layer
			if not self.first:
				x = self.relu(self.bn1(self.conv1(x)))

			y = F.interpolate(x, scale_factor=2, mode='trilinear', align_corners=False)
			y = self.relu(self.bn2(self.conv2(y)))

			y = torch.cat([prev, y], 1)
			y = self.relu(self.bn3(self.conv3(y)))

			return y

	# End Unet definition
	
	import copy
	net = copy.deepcopy(unet)
	num_classes = 7
	net.convd1.conv1 = ConvD(1,16,0.5,'gn',first=True)
	net.convd1.conv1.weight = nn.Parameter(unet.convd1.conv1.weight[:,1,:,:,:].unsqueeze(1))
	net.seg3 = nn.Conv3d(128, num_classes, kernel_size=(1,1,1), stride=(1,1,1))
	net.seg2 = nn.Conv3d(64, num_classes, kernel_size=(1,1,1), stride=(1,1,1))
	net.seg1 = nn.Conv3d(32, num_classes, kernel_size=(1,1,1), stride=(1,1,1))
	net.seg3.weight = nn.Parameter(net.seg3.weight)
	net.seg2.weight = nn.Parameter(net.seg2.weight)
	net.seg1.weight = nn.Parameter(net.seg1.weight)

	net.cpu()
	if gpu:
		net.cuda()

	reload_path = os.path.join(BASE, 'unet_model.pt')
	net.load_state_dict(torch.load(reload_path, map_location=torch.device(device)))


	del unet

	output_path = os.path.join(BASE, 'UNet_Outputs')
	if not os.path.exists(output_path):
		os.mkdir(output_path)
	net.eval()
	with torch.no_grad():
		''' Predict '''
		for k in range(len(scans_all)):
			name, info, inputs = next(data_gen)
			print(name)
			save_name = os.path.join(output_path, name[:name.find('.nii.gz')] + '.segmented.nii.gz')
			if os.path.exists(save_name):
				continue
			inputs_np = inputs.cpu().detach().numpy()
			in_mean = np.mean(inputs_np)
			in_std = np.std(inputs_np)
			output = net(inputs)
			n,c = output.shape[:2]
			N = output.shape[3]
			output = output.view(n,c,-1)
			lsoftmax = nn.LogSoftmax(dim=1)
			output = lsoftmax(output)
			output = output.argmax(dim=1)
			if n == 1:
				output = output.view(N,N,N1)
			else:
				output = output.view(n,N,N,N1)
			output = output.cpu().detach().numpy()
			output = resize(output, info[0], preserve_range=True, mode='constant', order=0, anti_aliasing=None)
			out_img = nib.Nifti1Image(output, info[1])
			nib.save(out_img, save_name)



