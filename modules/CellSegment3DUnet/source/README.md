
### Instructions for Segmentation Pipeline

- Data PNAS: VRL Data on [google drive](https://drive.google.com/drive/folders/1RvZYdojQGWGE1V6su1pZOOvJ0g0wKZLy)
- Data Purdue: Szymanski Lab data on google drive (in the same folder as above)

#### Workflow

##### Pre-requisites
- Background subtraction code in *.ijm file
- results are in background_subtracted folder

##### Histogram Match (with PNAS and Purdue Data)
- python2 hist_match.py
- celldataset.cell_testing('/source/data/celldata/') contains the background subtracted images
- celldataset.cell_training('/source/data/PNAS/') takes the PNAS dataset for training
- results in hist_match folder (z interpolation is done 5 times)

##### Predict
- python2 predict.py
- user model_last.tar file
- generates a probability map in prob_map folder
- uses pytorch, torchvision and scikit image

##### Post Processing 
- python2 postprocessing.py
- Enter Seeds as 15 and the threshold for black voxels as 0.05
- Hyperparams are in main function
- result folder has the output

-----------------------------------------------------

##### nvidia-docker [instructions](https://devblogs.nvidia.com/nvidia-docker-gpu-server-application-deployment-made-easy/)

###### Setup and test nvidia-docker as per https://github.com/NVIDIA/nvidia-docker
- Run "nvidia-persistenced" and verify its status
  - [root@HOST~]# systemctl status nvidia-persistenced.service
- docker run --runtime=nvidia --rm nvidia/cuda:9.0-base nvidia-smi
- nvidia-docker run --rm -ti nvidia/cuda:9.0-base bash
- Use a preset environment for development from https://github.com/ufoym/deepo
  - nvidia-docker run -it -v ${PWD}:/source --ipc=host ufoym/deepo bash

###### Start the container and run torch using DOckerfile
- Use the provided Dockerfile
  - nvidia-docker build -t torch-segmentation:latest . -f Dockerfile.pytorch-py36-py27-cu90
  - nvidia-docker run --name torch_vision -it -v ${PWD}:/source --ipc=host torch-segmentation:latest




