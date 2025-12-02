import cv2
import os
from detection import canny_detector

# input_path_dict will have input file paths with keys corresponding to the input names set in the cli.
def run_module(input_path_dict, output_folder_path, min_hysteresis=100, max_hysteresis=200):
    """
    This function should load input resources from input_path_dict, do any pre-processing steps, run the algorithm,
    save all outputs to output_folder_path, AND return the outputs_path_dict.
    
    :param input_path_dict: Dictionary of input resource paths indexed by input names. 
    :param output_folder_path: Directory where to save output results.
    :param min_hysteresis: Tunable parameter must have default values.
    :param max_hysteresis: Tunable parameter  must have default values.
    :return: Dictionary of output result paths.
    """
    
    ##### Preprocessing #####

    # Get input file paths from dictionary
    input_img_path = input_path_dict['Input Image'] # KEY MUST BE DESCRIPTIVE, UNIQUE, AND MATCH INPUT NAME SET IN CLI

    # Load data
    img = cv2.imread(input_img_path, 0)

    ##### Run algorithm #####

    edges_detected = canny_detector(img, min_hysteresis, max_hysteresis)


    ##### Save output #####

    # Get filename
    input_img_name = os.path.split(input_img_path)[-1][:-4]

    # Generate desired output file names and paths
    output_img_path = "%s/%s_out.jpg" % (output_folder_path, input_img_name) # CHECK FILE EXTENSION!

    # Save output files
    cv2.imwrite(output_img_path, edges_detected)

    # Create dictionary of output paths
    output_paths_dict = {}
    output_paths_dict['Output Image'] = output_img_path  # KEY MUST BE DESCRIPTIVE, UNIQUE, AND MATCH OUTPUT NAME SET IN CLI

    ##### Return output paths dictionary #####  -> IMPORTANT STEP
    return output_paths_dict

if __name__ == '__main__':
    # Place some code to test implementation
    
    # Define input_path_dict and output_folder_path
    input_path_dict = {}
    current_directory = os.getcwd()
    # Place test image in current directory
    input_path_dict['Input Image'] = os.path.join(current_directory,'img.jpeg') # KEY MUST MATCH INPUT NAME SET IN CLI
    output_folder_path = current_directory
    
    # Run algorithm and return output_paths_dict
    output_paths_dict = run_module(input_path_dict, output_folder_path, min_hysteresis=100, max_hysteresis=200)
    
    # Get outPUT file path from dictionary
    output_img_path = output_paths_dict['Output Image'] # KEY MUST MATCH OUTPUT NAME SET IN CLI
    # Load data
    out_img = cv2.imread(output_img_path, 0)
    # Display output image and ensure correct output
    # cv2.imshow("Results",out_img)