"""
Given an input image, predict the location of removed and inserted
seams in the input image and generate an overall manipulation score
indicating if the image is seam carved or not.

@authors: Erik Rosten, Chandrakanth Gudavalli
contact: <erik@mayachitra.com>, <gudavalli@mayachitra.com>
"""

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Avoid printing Warning messages

import argparse
import sys

import matplotlib.pyplot as plt
import numpy as np, cv2

def add_path(path):
    if path not in sys.path:
        sys.path.insert(0, path)
add_path(os.path.join(os.path.dirname(__file__), 'helper_modules'))

from detectors import load_models, detect_sc, get_overall_score
from validations import isvalid

from img_loader import load_img

##########################################################
# Function to parse all the commandline arguments
##########################################################
def parse_args():
    
    parser = argparse.ArgumentParser(description='Check if the image is seam carved.')

    parser.add_argument(
    '--input_fname',
        help='Input image',
        default="data/sample_manipulations/xview1_object_removal/manipulated_image.png",
        type=str
    )

    parser.add_argument(
        '--srdetector',
        dest='model_fname_sr_detector',
        help='Deep learning model with .h5 extension for seam removal detection',
        default="models/efficientnetb7_based_sr_detector_xview2_dataset.h5",
        type=str
    )

    parser.add_argument(
        '--sidetector',
        dest='model_fname_si_detector',
        help='Deep learning model with .h5 extension for seam insertion detection',
        default="models/efficientnetb7_based_si_detector_all_datasets.h5",
        type=str
    )

    parser.add_argument(
        '--stage2model',
        dest='model_fname_stage2',
        help='Deep learning model with .h5 extension for image level classification (stage 2)',
        default="models/stage2_binary_classifier.h5",
        type=str
    )
    
    parser.add_argument(
        '--output_fname',
        help='Output Image showing the heatmap and the input image',
        default="output/prediction_output_dockerized.png",
        type=str
    )

    # if len(sys.argv) == 1:
    #     parser.print_help()
    #     sys.exit(1)
    
    return parser.parse_args()

def get_all_args():
    # Parse all the commandline arguments
    args = parse_args()

    if not isvalid(args):
        quit()


def run_module(input_path_dict, output_folder_path, bq=None):

    input_data = {
        "input_fname": input_path_dict["Input Image"],
        "model_fname_sr_detector": "models/efficientnetb7_based_sr_detector_xview2_dataset.h5",
        'model_fname_si_detector': "models/efficientnetb7_based_si_detector_all_datasets.h5",
        'model_fname_stage2': "models/stage2_binary_classifier.h5",
        'output_fname': os.path.join(output_folder_path, "prediction_output_dockerized.png") #input_path_dict["output_fname"],
    }
    args = input_data

    # output_folder_path = os.path.split(input_path_dict['output_fname'])[0]

    ##########################################################
    # Predict Heatmap
    ##########################################################
    img_path = args["input_fname"]
    ckp_file_path_sr_detector = args["model_fname_sr_detector"]
    ckp_file_path_si_detector = args["model_fname_si_detector"]

    #Load Image
    img = load_img(img_path)
    print("Image Loaded")

    if img is None:
        quit()

    if img.shape[0] < 512 or img.shape[1] < 512:
        print("Error: Image should have at least 512 rows and 512 columns.")
        quit()

    if len(img.shape)!=3 or img.shape[2] != 3:
        print("Error: Image must have 3 channels.")
        quit()

    # Load Seam Removal and Seam Insertion Detector
    print("Loading models...")
    bq.update_mex('Loading models...')
    model_loaded_sr_detect, model_loaded_si_detect = load_models(ckp_file_path_sr_detector, ckp_file_path_si_detector)

    bq.update_mex('Running Detections...')
    pred_results = detect_sc(img, model_loaded_sr_detect, model_loaded_si_detect)

    ##########################################################
    # Run Stage2 on center crop
    ##########################################################

    overall_score = get_overall_score(pred_results, img, args["model_fname_stage2"])

    print("Overall Manipulation Score (0:Pristine, 1:Manipulated):",overall_score)

    ##########################################################
    # Save heatmap to args.output_fname
    ##########################################################
    aspect_ratio = img.shape[0]/img.shape[1]
    if 0.8 <= aspect_ratio <= 1.2:
        fig = plt.figure(figsize=(15,8))
    elif aspect_ratio > 1.2:
        fig = plt.figure(figsize=(15,10))
    elif aspect_ratio < 0.8:
        fig = plt.figure(figsize=(15,6))

    plt.subplot (121)
    plt.title('Input Image')
    plt.imshow(img)

    plt.subplot(122)
    plt.title("Predicted Mask \n Red:Removed Seams; Green:Inserted Seams")
    plt.imshow(pred_results, cmap="gray", vmin=0, vmax=1)

    plt.suptitle("Overall Manipulation Score (0:Pristine, 1:Manipulated): "+str(overall_score), y=0.98)

    out_dir = os.path.split(str(args["output_fname"]))[0]
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    plt.savefig(str(args["output_fname"]), bbox_inches='tight')

    print("Output has been saved to '"+args["output_fname"]+"'.")

    outputs_path_dict = {}
    outputs_path_dict['Output Image'] = str(args["output_fname"])

    bq.update_mex('Completed')

    return outputs_path_dict


if __name__ == '__main__':
    input_path_dict = {
        "Input Image": "/home/chandrakanth/Desktop/ck_code/bisque_deployment_july_6th/Modules/SeamCarvingDetection/data/sample_manipulations/manipulated/manipulated_xview2_object_dislocation.png",
    }
    current_directory = os.getcwd()

    # Run algorithm and return output_paths_dict
    outputs_path_dict = run_module(input_path_dict, "output")

    # Get outPUT file path from dictionary
    output_img_path = outputs_path_dict['Output Image']

    # Load data
    out_img = cv2.imread(output_img_path, 0)
    # Display output image and ensure correct output
    # cv2.imshow("Results",out_img)
