
This module is used for Mask R-CNN 

#### Pre-requisite:

- Mask RCNN source should be present and should have compiled pycoco tools available in source/samples/coco/ folder
  - Download the repo and build it
  - cd ~/source/ && wget https://github.com/matterport/Mask_RCNN/releases/download/v2.0/mask_rcnn_coco.h5
  - python3 setup.py install
  - cd samples/coco && git clone https://github.com/cocodataset/cocoapi
  - cd cocoapi/PythonAPI/ && make
  - cp -r pycocotools/ ../../ 
- This uses the Python 3 converted BQAPI codebase. Achieved using "2to3.5 -w *.py"
- Make sure mrcnn is installed within the container using "python3 setup.py install"

### Build the Module
```
docker build -t biodev.ece.ucsb.edu:5000/tflow-mrcnn-mod-v1:latest . -f Dockerfile
```

### Run the Module (Make sure Nvidia-docker is installed and default runtime is nvidia)
```
docker run -it --ipc=host -v $(pwd):/module  biodev.ece.ucsb.edu:5000/tflow-mrcnn-mod-v1:latest bash
```

### Tag & Push
```
docker tag $(docker images -q "biodev.ece.ucsb.edu:5000/tflow-mrcnn-mod-v1:latest") biodev.ece.ucsb.edu:5000/tflow-mrcnn-mod-v1:latest
docker push biodev.ece.ucsb.edu:5000/tflow-mrcnn-mod-v1:latest
```

### Test Runs 

TODO: Need to fix the parameters in the arguments:

```
python PythonScriptWrapper.py \
 http://drishti.ece.ucsb.edu:8080/data_service/00-FR5xa2YPb2aGYXSwPqqyVY \
 15 0.05 \
 http://drishti.ece.ucsb.edu:8080/module_service/mex/00-AiYVox9kzJTeqHdsHtZQdf \
 admin:00-AiYVox9kzJTeqHdsHtZQdf
```

### TODO
- How to integrate with Python 3 codebase
  - Use a Python 3 wheels build of the bisque-api==0.5.9 package
  - BQAPI https://setuptools.readthedocs.io/en/latest/setuptools.html#distributing-a-setuptools-based-project
  ```
  cd ~/bisque/bqapi
  python3 -m pip install --user --upgrade setuptools wheel
  python3 setup.py sdist bdist_wheel
  ```
  - This will create the whl file in dist folder which can be installed using
  ```
  python3 -m pip install dist/bisque_api-0.5.9-py2.py3-none-any.whl 
  ```
  - In case the bqapi code is not portable to Python 3 easily. We can use the 2to3.5 CLI for migration. This will update the files with Python 3 syntax in place and move the legacy code to a *.bak file upon update
  ```
  2to3.5 -w *.py  
  ```
  - Ideally we should be able to create a new bisque-api-py3 and push it to the packages respository at https://biodev.ece.ucsb.edu/py/bisque/prod
