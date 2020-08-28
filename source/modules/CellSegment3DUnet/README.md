This module is used for segmenting the 3D image using UNet Pytorch based model. It works out of the docker image and all the corresponding data & code should be made available inside the docker image.

#### Pre-requisite:
- Source should be present and should have compiled data & model available in respective folder
  - Download the data from https://drive.google.com/open?id=1WsMfVIdNaLqTrAPkt_qNdNyNSpINSVxS
  - unzip its contents to folder source/data/PNAS
 
#### Create Docker Instance
docker build -t biodev.ece.ucsb.edu:5000/torch-cellseg-3dunet-v2:latest . -f Dockerfile

```
docker tag $(docker images -q "biodev.ece.ucsb.edu:5000/torch-cellseg-3dunet-v2:latest") biodev.ece.ucsb.edu:5000/torch-cellseg-3dunet-v2:latest
docker push biodev.ece.ucsb.edu:5000/torch-cellseg-3dunet-v2:latest
```

#### Run instance and bash
docker run -it --ipc=host  biodev.ece.ucsb.edu:5000/torch-cellseg-3dunet-v2:latest bash

```
The docker run template creates a container and then runs it 
```

```
docker create --ipc=host  biodev.ece.ucsb.edu:5000/torch-cellseg-3dunet-v2 \
python PythonScriptWrapper.py \
http://loup.ece.ucsb.edu:8088/data_service/00-DJW3jb8FDp9njehRm9qkMf \
/DataContainers/SyntheticVolumeDataContainer/CellData/Phases \ 
http://loup.ece.ucsb.edu:8088/module_service/mex/00-eo84f3owtxyRRU25JxSxMf \
admin:00-eo84f3owtxyRRU25JxSxMf


python PythonScriptWrapper.py http://loup.ece.ucsb.edu:8088/data_service/00-DJW3jb8FDp9njehRm9qkMf /DataContainers/SyntheticVolumeDataContainer/CellData/Phases http://loup.ece.ucsb.edu:8088/module_service/mex/00-eo84f3owtxyRRU25JxSxMf admin:00-eo84f3owtxyRRU25JxSxMf
```

#### Run based on the hash identifier

```
docker start 9eb7d1be403ca77b6cdc5c2140d289c2ee1692e736fe39abc0bf1fd798a530f9
```