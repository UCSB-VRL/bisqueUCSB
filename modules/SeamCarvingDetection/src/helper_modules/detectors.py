import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Avoid printing Warning messages
import sys

import numpy as np

import tensorflow as tf
from unet_models import get_model_by_name

from skimage.util import view_as_windows

def load_models(ckp_file_path, ckp_file_path_si_detector):
	try:
	    def add_path(path):
	        if path not in sys.path:
	            sys.path.insert(0, path)
	    this_dir = os.path.dirname(__file__)
	    # Add libs to PYTHONPATH
	    lib_path = os.path.join(this_dir, 'helper_modules')
	    add_path(lib_path)
	    
	    
	    
	    model_params = {
	                    'output_channels': 1,
	                    'pretrained': False
	    }
	    model_loaded_sr_detect = get_model_by_name("efficientnetb7", model_params)
	    model_loaded_sr_detect.load_weights(ckp_file_path)

	    model_loaded_sr_detect.compile(optimizer=tf.keras.optimizers.Adam(lr=0.0001),
	              loss="mse",
	              metrics=['accuracy'])
	except:
	    model_loaded_sr_detect = tf.keras.models.load_model(ckp_file_path)
	print("Loaded Seam Removal Detector.")

	# Load Seam Insertion Detector
	try:
	    model_loaded_si_detect = get_model_by_name("efficientnetb7", model_params)
	    model_loaded_si_detect.load_weights(ckp_file_path_si_detector)

	    model_loaded_si_detect.compile(optimizer=tf.keras.optimizers.Adam(lr=0.0001),
	                          loss="mse",
	                          metrics=['accuracy'])
	except:
	    model_loaded_si_detect = tf.keras.models.load_model(ckp_file_path_si_detector)
	print("Loaded Seam Insertion Detector.")

	return model_loaded_sr_detect, model_loaded_si_detect

def detect_on_patch(img, model_loaded_sr_detect, model_loaded_si_detect):
	#Covert image to a format comaptible to tensorflow for faster processing
	dim = (int(img.shape[0]/32.0)*32,int(img.shape[1]/32.0)*32,3)
	X = np.empty((1, *dim))

	##########################################################
	# Vertical seam carving detection
	##########################################################
	print('Vertical seam carving detection:')
	X[0,] = img[0:dim[0],0:dim[1],:] # Crop images to a dimension divisible by 32 for UNet compatibility

	#Predict heatmap
	print('Prediction mask being generated by Seam Removal Detector...')
	results_sr_vert = model_loaded_sr_detect.predict(X)[0,:,:,0]

	print('Prediction mask being generated by Seam Insertion Detector...')
	results_si_vert = model_loaded_si_detect.predict(X)[0,:,:,0]

	##########################################################
	# Horizontal seam carving detection
	##########################################################
	print('Horizontal seam carving detection:')
	# dim = (dim[1],dim[0],dim[2])
	X = np.empty((1, dim[1],dim[0],dim[2]))
	X[0,] = np.rot90(img)[0:dim[1],0:dim[0],:]

	#Predict heatmap
	print('Prediction mask being generated by Seam Removal Detector...')
	results_sr_hori = model_loaded_sr_detect.predict(X)[0,:,:,0]
	results_sr_hori = np.rot90(results_sr_hori, -1)

	print('Prediction mask being generated by Seam Insertion Detector...')
	results_si_hori = model_loaded_si_detect.predict(X)[0,:,:,0]
	results_si_hori = np.rot90(results_si_hori, -1)

	print('***************************')

	return results_sr_vert, results_si_vert, results_sr_hori, results_si_hori

def detect_sc(img, model_loaded_sr_detect, model_loaded_si_detect, thresh=0.5):
	dim = (int(img.shape[0]/32.0)*32,int(img.shape[1]/32.0)*32,3)
	if img.shape[0]*img.shape[1] <= 1024*1024:
		results_sr_vert, results_si_vert, results_sr_hori, results_si_hori = \
		detect_on_patch(img, model_loaded_sr_detect, model_loaded_si_detect)
	else:
		# For larger images, divide image into patches of size 512x512 and
		# run detector separately on each ptach.
		col_start_list = list()
		for i in range(dim[1]//512):
			col_start_list.append(i*512)
		col_start_list.append(dim[1])

		row_start_list = list()
		for i in range(dim[0]//512):
			row_start_list.append(i*512)
		row_start_list.append(dim[0])

		print("Dividing image into patches of size 512x512...")
		results_sr_vert = np.zeros((dim[0], dim[1]), dtype=np.float64)
		results_sr_hori = np.zeros((dim[0], dim[1]), dtype=np.float64)
		results_si_vert = np.zeros((dim[0], dim[1]), dtype=np.float64)
		results_si_hori = np.zeros((dim[0], dim[1]), dtype=np.float64)
		patch_count = 0
		for row_i in range(1,len(row_start_list)):
			for col_i in range(1,len(col_start_list)):
				patch_count += 1
				print("Working on patch-"+str(patch_count)+"/"+str((len(row_start_list)-1)*(len(col_start_list)-1)))
				row_start = row_start_list[row_i-1]
				row_end = row_start_list[row_i]
				col_start = col_start_list[col_i-1]
				col_end = col_start_list[col_i]
				
				patch_res = detect_on_patch(img[row_start:row_end,col_start:col_end, :], 
								model_loaded_sr_detect, model_loaded_si_detect)

				results_sr_vert[row_start:row_end,col_start:col_end], results_si_vert[row_start:row_end,col_start:col_end], \
				results_sr_hori[row_start:row_end,col_start:col_end], results_si_hori[row_start:row_end,col_start:col_end] = patch_res

	sr_detection_res = np.maximum(results_sr_vert, results_sr_hori)
	si_detection_res = np.maximum(results_si_vert, results_si_hori)

	pred_results = np.zeros(img.shape)
	pred_results[:dim[0],:dim[1],0] = ((sr_detection_res>thresh)*1).astype(int)
	pred_results[:dim[0],:dim[1],1] = ((si_detection_res>thresh)*1).astype(int)

	return pred_results

def get_score_using_sc(heatmap, thresh = 0.5):
    
    def add_path(path):
        if path not in sys.path:
            sys.path.insert(0, path)
    this_dir = os.path.dirname(__file__)
    # Add libs to PYTHONPATH
    lib_path = os.path.join(this_dir, 'image_seam_carver')
    add_path(lib_path)
    from image_seam_carver.image_resizing.seam_carving_image_resizing import get_first_seam_boolmask
    
    p_mask_ver = np.zeros(heatmap.shape)
    np.putmask(p_mask_ver, heatmap < thresh, 255)

    hmap_with_seams, seam_boolmask = get_first_seam_boolmask(np.dstack((heatmap,heatmap,heatmap))*255, 
                                                             keep_mask = p_mask_ver, num_remove=1)
    seam_boolmask = (seam_boolmask==False)*1.0
    pixel_count = np.multiply(seam_boolmask, (heatmap>thresh)).sum()
    vert_score = pixel_count*1.0/heatmap.shape[0]

    hmap_with_seams, seam_boolmask = get_first_seam_boolmask(np.rot90(np.dstack((heatmap,heatmap,heatmap))*255), 
                                                             keep_mask = np.rot90(p_mask_ver), num_remove=1)
    seam_boolmask = (seam_boolmask==False)*1.0
    pixel_count = np.multiply(seam_boolmask, (np.rot90(heatmap)>thresh)).sum()
    hori_score = pixel_count*1.0/heatmap.shape[1]

    # print((hori_score, vert_score))
    overall_score = max(hori_score, vert_score)
    return overall_score

def get_overall_score(pred_results, img, model_fname_stage2, thresh=0.5):
	model_loaded = tf.keras.models.load_model(model_fname_stage2)

	#Covert image to a format comaptible to tensorflow for faster processing
	#Run stage2 prediction on every non overlapping 512x512 patch
	patchsize_row = 512
	patchsize_col = 512
	stride = 512

	aswindows = view_as_windows(pred_results.copy(), (patchsize_row, patchsize_col, 3), step=stride)
	X = aswindows.reshape((aswindows.shape[0]*aswindows.shape[1],patchsize_row,patchsize_col,3)).copy()

	#Predict heatmap
	print('Computing scores')
	y = model_loaded.predict(X)[:,0]
	# print(y)

	# Logic to calculate image level manipulation score
	if len(y) <= 4:
		# For smaller images, patches along atelast one dimension
		# needs to be flagged
		count = (y > thresh).sum() #len(np.where(y > thresh))
		if count >= min(img.shape[0:2])//512:
			overall_score = np.round(max(abs(y)),2)
		else:
			overall_score = np.round(min(abs(y)),2)
	else:
		y = y.reshape((aswindows.shape[0], aswindows.shape[1]))
		y = np.repeat(y, patchsize_col, axis=1).repeat(patchsize_row, axis=0)

		# import cv2
		# cv2.imwrite("stage2_hmap.png",(y>thresh)*255)

		overall_score = get_score_using_sc(y)

	return overall_score