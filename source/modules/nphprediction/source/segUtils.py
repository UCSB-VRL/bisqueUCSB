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
import nibabel as nib
import pickle
import os
import warnings
from skimage.draw import ellipse
from cv2 import fastNlMeansDenoising as denoising
from scipy.ndimage import binary_dilation as dilation
from scipy.ndimage import binary_erosion as erosion
from scipy.ndimage import binary_opening as opening
from scipy.ndimage import binary_closing as closing
from sklearn.ensemble import RandomForestClassifier
from skimage.draw import ellipse
from skimage.filters import gaussian, median
from skimage.morphology import disk, convex_hull_image
from skimage.segmentation import morphological_chan_vese as mcv
from joblib import Parallel, delayed
from scipy.ndimage import binary_fill_holes as fill_holes


def threshold(BASE, folder, parallel):
	'''
	Classification of tissue types in CT scan.
	'''
	classifier_name = os.path.join(BASE, 'TissueClassifier.pkl')
	if not os.path.exists(os.path.join(BASE, 'Thresholds')):
		os.mkdir(os.path.join(BASE, 'Thresholds'))
	#load tissue classifier
	with open(classifier_name, 'rb') as f:
		clf = pickle.load(f)
	fpath = os.path.join(BASE,folder)
	imnames = [os.path.join('source/Scans', f) for f in os.listdir(fpath) if (f.endswith('.nii.gz') or f.endswith('.nii'))]
	print(imnames)
	imnames.sort()
	with open(os.path.join(BASE, 'imname_list.pkl'), 'wb') as f:
		pickle.dump(imnames, f)

	# Apply Threshold
	print('-------- Applying Threshold --------')
	def apply_thresh(i):
		imname = imnames[i]
		imname_short = os.path.split(imname)[-1]
		print(imname_short)
		threshold_namev = os.path.join(BASE, 
									'Thresholds', 
									imname_short[:imname_short.find('.nii.gz')] +'.thresholdedv.nii.gz')
		threshold_namec = os.path.join(BASE,
									'Thresholds',
									imname_short[:imname_short.find('.nii.gz')] +'.thresholdedc.nii.gz')
		short_tnamev = os.path.split(threshold_namev)[-1]
		short_tnamec = os.path.split(threshold_namec)[-1]
		if short_tnamev in os.listdir(os.path.join(BASE, 'Thresholds')):
			if short_tnamec in os.listdir(os.path.join(BASE, 'Thresholds')):
				return
		if not os.path.exists(imname):
			print('does not exist')
			return
		im = nib.load(imname)
		image = im.get_data()
		image[np.where(image > 127)] = 127
		image[np.where(image < -128)] = -1000
		#denoising
		for s in range(0, image.shape[2]):
			slic = image[:,:,s]
			slic = np.uint8(slic)
			slic = denoising(slic, h=5)
			image[:,:,s] = np.float64(slic)
		#done denoising
		affine = im.affine
		header = im.header
		xsize, ysize, zsize = image.shape
		x = image.flatten()
		x_predict = x.reshape(-1,1)
		x_predict = x_predict.astype(float)
		y = clf.predict(x_predict)
		skull = np.copy(y)
		yv = np.copy(y)
		yc = np.copy(y)
		yv[np.where(yv != 1)[0]] = 0
		yc[np.where(yc != 2)[0]] = 0
		yc[np.where(yc == 2)[0]] = 1
		skull[np.where(skull != 3)[0]] = -1
		skull[np.where(skull == 3)[0]] = 1
		threshold_imgv = yv.reshape(image.shape)
		threshold_imgc = yc.reshape(image.shape)
		skull_img = skull.reshape(image.shape)
		structure = np.array([[1,1,1],[1,1,1],[1,1,1]])
		threshold_imgv[np.where(threshold_imgv < 0.5)] = -1
		threshold_imgv[np.where(threshold_imgc > 0.5)] = -1
		threshold_imgc[np.where(threshold_imgc < 0.5)] = -1
		threshold_imgc[np.where(threshold_imgv > 0.5)] = -1
		skull_name = os.path.join(BASE, 
								'Thresholds', 
								imname_short[:imname_short.find('.nii.gz')]+'.skull.nii.gz')
		nii_imagev = nib.Nifti1Image(threshold_imgv.astype(np.float32), affine, header)
		nii_imagec = nib.Nifti1Image(threshold_imgc.astype(np.float32), affine, header)
		skull_image = nib.Nifti1Image(skull_img.astype(np.float32), affine, header)
		nib.save(nii_imagev, threshold_namev)
		nib.save(nii_imagec, threshold_namec)
		nib.save(skull_image, skull_name)
		print('done thresholding: ' + imname)

	if parallel:
		Parallel(n_jobs=4)(delayed(apply_thresh)(i) for i in range(0, len(imnames)))
	else:
		for i in range(0, len(imnames)):
			apply_thresh(i)


def subarachnoid_seg(BASE, parallel):
	'''
	Segments the subarachnoid space after white matter and ventricle segmentation.
	'''
	print('---------------- Subarachnoid Segmentation ------------------')
	imnames = pickle.load(open(os.path.join(BASE,'imname_list.pkl'), 'rb'))
	imnames.sort()

	def subseg(i):
		imname = imnames[i]
		imname_short = os.path.split(imname)[-1]
		print(imname_short)
		threshold_name = os.path.join(BASE, 'UNet_Outputs', imname_short[:imname_short.find('.nii.gz')] + '.segmented.nii.gz')
		new_name = os.path.join(BASE, 'Thresholds', imname_short[:imname_short.find('.nii.gz')] + '.brain.nii.gz')
		if not os.path.exists(threshold_name):
			print('skipped due to no threshold')
			return
		threshold_image = nib.load(threshold_name)
		threshold_array = threshold_image.get_data()
		threshold_namev = os.path.join(BASE,
									'Thresholds',
									imname_short[:imname_short.find('.nii.gz')] + '.thresholdedv.nii.gz')
		threshold_imagev = nib.load(threshold_namev)
		varray = threshold_imagev.get_data()
		final_pred = 'UNet_Outputs'
		segment_name = os.path.join(BASE,
									final_pred,
									imname_short[:imname_short.find('.nii.gz')] + '.segmented.nii.gz')
		#orig_vname = os.path.join(BASE,
		#							'Predictions',
		#							imname_short[:imname_short.find('.nii.gz')] + '.segmentedv150.nii.gz')
		new_segname = segment_name[:segment_name.find('.nii.gz')] + '1.nii.gz'
		if not os.path.exists(segment_name):
			print('skipped due to no segment')
			return
		if os.path.exists(new_segname):
			return
		segment_img = nib.load(segment_name)
		segment_array = segment_img.get_data()
		#orig_vimg = nib.load(orig_vname)
		#orig_varray = orig_vimg.get_data()
		thresh_filled = np.copy(threshold_array)
		thresh_filled[np.where(threshold_array<0)] = 0
		thresh_filled[np.where(segment_array>0)] = 1

		c_matter_z = np.where(segment_array==2)[2]
		if c_matter_z.size == 0:
			print('skipping due to no vent in segment')
			return
		r = range(c_matter_z.min(), c_matter_z.max())

		for s in r:
			slic = thresh_filled[:,:,s]
			slic = fill_holes(slic)
			thresh_filled[:,:,s] = slic
		for s in range(0, thresh_filled.shape[2]):
			slic = thresh_filled[:,:,s]
			with warnings.catch_warnings():
				warnings.simplefilter("ignore")
				slic = convex_hull_image(slic)
			thresh_filled[:,:,s] = slic
		subarray = np.copy(varray)
		subarray[np.where(segment_array > 0)] = 0
		subarray[np.where(thresh_filled < 0.5)] = 0
		varray[np.where(segment_array > 0)] = -1
		varray[np.where(thresh_filled < 0.5)] = -1

		new_thresholdv = nib.Nifti1Image(varray, threshold_imagev.affine, threshold_imagev.header)
		new_tnamev = os.path.join(BASE,
								'Thresholds',
								imname_short[:imname_short.find('.nii.gz')] + '.thresholdedv1.nii.gz')
		nib.save(new_thresholdv, new_tnamev)

		segment_array[np.where(subarray > 0.5)] = 3
		segment_array[np.where((varray==1) & (segment_array==1))] = 3

		segment_img = nib.Nifti1Image(segment_array, segment_img.affine, segment_img.header)
		filled_image = nib.Nifti1Image(thresh_filled, threshold_image.affine, threshold_image.header)
		nib.save(filled_image, new_name)
		nib.save(segment_img, new_segname)

	r = range(0, len(imnames))
	if parallel:
		Parallel(n_jobs=5)(delayed(subseg)(i) for i in r)
	else:
		for k in r:
			subseg(k)


def train_tissue_classifier(BASE, classifier_name='TissueClassifier.pkl'):
	'''
	Trains Random Forest classifier to classify tissue types.
	To use, place labeled masks in folder named 'Classifiers' with name matching the corresponding images in the
	'Scans' folder, but with the name ending in 'RFSeg.nii.gz' instead of '.nii.gz'.
	'''
	x = []
	y = []
	seg_image_names = [name for name in os.listdir(os.path.join(BASE, 'Classifiers')) if name.endswith('RFSeg.nii.gz')]
	for i in range(0,len(seg_image_names)):
		seg_image_name = seg_image_names[i]
		image_name = seg_image_name[:seg_image_name.find('.RFSeg.nii.gz')] + '.nii.gz'
		print(image_name)
		image = nib.load(os.path.join(BASE, 'Scans', image_name))
		seg_image = nib.load(os.path.join(BASE, 'Classifiers', seg_image_name))
		np_image = image.get_data()
		np_segimage = seg_image.get_data()
		#foreground = np_image[np.where(np_image > -500)]
		classes = np.unique(np_segimage)[1:]
		for c in classes:
			xind, yind, zind = np.where(np_segimage==c)
			for i in range(0, xind.shape[0]):
				x.append(np_image[xind[i],yind[i],zind[i]])
				y.append(c)
	x = np.array(x)
	print(x.shape)
	x = x.reshape(-1,1)
	y = np.array(y)
	x = x.astype(float)
	y = y.astype(float)
	clf = RandomForestClassifier(n_estimators=30, max_depth=30)
	clf.fit(x, y)
	with open(os.path.join(BASE, classifier_name), 'wb') as f:
		pickle.dump(clf, f)

