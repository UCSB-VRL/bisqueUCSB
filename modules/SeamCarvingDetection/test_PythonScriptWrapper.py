# standardized naming convention for running modules.
from src.BQ_run_module import run_module
import os

input_path_dict = {
        "Input Image": "/home/chandrakanth/Desktop/ck_code/bisque_deployment_july_6th/Modules/SeamCarvingDetection/data/sample_manipulations/xview1_object_removal/manipulated_image.png",
    }

# Run algorithm and return output_paths_dict
outputs_path_dict = run_module(input_path_dict, "output")

print(outputs_path_dict)