#!/usr/bin/env python
# coding: utf-8

# # Mask R-CNN Client
# 
# A quick client to detect and segment objects.

import os
import sys
import random
import math
import numpy as np
import skimage.io
import matplotlib
import matplotlib.pyplot as plt


# Root directory of the project
ROOT_DIR = os.path.abspath("./")

# Import Mask RCNN
sys.path.append(ROOT_DIR)  # To find local version of the library
from mrcnn import utils
import mrcnn.model as modellib
from mrcnn import visualize
# Import COCO config
sys.path.append(os.path.join(ROOT_DIR, "source/samples/coco/"))  # To find local version
import coco

# Directory to save logs and trained model
MODEL_DIR = os.path.join(ROOT_DIR, "source/logs")

# Local path to trained weights file
COCO_MODEL_PATH = os.path.join(ROOT_DIR, "source/mask_rcnn_coco.h5")
# Download COCO trained weights from Releases if needed
if not os.path.exists(COCO_MODEL_PATH):
    utils.download_trained_weights(COCO_MODEL_PATH)

# ## Configurations
# 
# We'll be using a model trained on the MS-COCO dataset. The configurations of this model are in the ```CocoConfig``` class in ```coco.py```.
# 
# For inferencing, modify the configurations a bit to fit the task. To do so, sub-class the ```CocoConfig``` class and override the attributes you need to change.

class InferenceConfig(coco.CocoConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1

config = InferenceConfig()
config.display()

# ## Create Model and Load Trained Weights
# Create model object in inference mode.
model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)

# Load weights trained on MS-COCO
model.load_weights(COCO_MODEL_PATH, by_name=True)

# COCO Class names
# Index of the class in the list is its ID. For example, to get ID of
# the teddy bear class, use: class_names.index('teddy bear')
class_names = ['BG', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
               'bus', 'train', 'truck', 'boat', 'traffic light',
               'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird',
               'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear',
               'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
               'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
               'kite', 'baseball bat', 'baseball glove', 'skateboard',
               'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
               'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
               'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
               'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
               'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
               'keyboard', 'cell phone', 'microwave', 'oven', 'toaster',
               'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
               'teddy bear', 'hair drier', 'toothbrush']

""" Param: test image file path  """
def detect(ffilepath):
    image = skimage.io.imread(ffilepath)
    # Run detection
    results = model.detect([image], verbose=1)
    # Visualize results
    r = results[0]
    return image, r


""" Params: image, results, output_file """
def fsave(image, r, outfile):
    print((r['rois']))
    print(("Output to file: ", outfile))
    visualize.display_instances(image, r['rois'], r['masks'], r['class_ids'], class_names, r['scores'], save_fig=outfile)

""" Main entry point for the test code """
if __name__== "__main__":
    # Directory of images to run detection on
    IMAGE_DIR = os.path.join(ROOT_DIR, "source/images")
    # Load a random image from the images folder
    file_names = next(os.walk(IMAGE_DIR))[2]
    file_name = random.choice(file_names)
    image, r = detect(os.path.join(IMAGE_DIR, file_name))
    print("--------------------------RESULT----------------------------------")
    print(("Image:",IMAGE_DIR,"/",file_name))
    print(("ROI:", r['rois'].shape))
    print(("Masks:", r['masks'].shape))
    print(("Class Ids:",r['class_ids']))
    print(("Scores:",r['scores']))
    print("------------------------------------------------------------------")
    fsave(image, r, outfile="mask_"+file_name)


