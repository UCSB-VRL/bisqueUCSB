# BQAPI


#### PIP Install {-}
```python
pip install -i https://biodev.ece.ucsb.edu/py/bisque/prod/+simple bisque_api
```

***

BQAPI provides bisque users with a means to extract features from resources using the feature service. Below is information on the Python API and a few example on how to use it.

> `FeatureResource(image=None, mask=None, gobject=None)`

Named tuple to make it easier to organize resources. Of course, one can always just make a simple list of tuples for the resource list.

> `class Feature()`

The Feature class is the base implementation of the feature service API for when one need to extract a set of features on a small set of resources. BQSession is used as the communication layer for bqfeatures, therefore before making any requests a local BQSession has to be instantiated to pass to any feature request.

> `fetch(session, name, resource_list, path=None)`

Requests the feature server to calculate features on provided resources.

__Input__

  - session - a local instantiated BQSession attached to a MEX.
  - name - the name of the feature one wishes to extract.
  - resource_list - list of the resources to extract. Format: [(`image_url`, `mask_url`, `gobject_url`),...] if a parameter is not required just provided None.
  - path - the location were the HDF5 file is stored. If None is set, the file will be placed in a temporary file and a Pytables file handle will be returned. (default: None)

__Output__

  - return - returns either a Pytables file handle or the file name when the path is provided

Lets upload an image an calculate a single feature on it.

```python
import os
from bqapi.comm import BQSession
from bqapi.bqfeature import Feature, FeatureResource

# initialize local session
session = BQSession().init_local(user, pwd, bisque_root='http://bisque.ece.ucsb.edu') 

#post image to bisque and get the response
response_xml = session.postblob('myimage.jpg') 

#construct resource list of the image just uploaded
resource_list = [FeatureResource(image='http://bisque.ece.ucsb.edu/image_service/%s' % response_xml.attrib['resource_uniq'])]

#fetch features on image resource
pytables_response = Feature().fetch(session, 'HTD', resource_list)

#get a numpy list of features for the downloaded HDF5 file.
feature = pytables_response.root.values[:]['feature']

#close and remove the HDF5 file since it is stored in a tempfile
pytables_response.close()
os.remove(pytables_response.filename)
```


> `fetch_vector(session, name, resource_list)`

Requests the feature server to calculate features on provided resources. Designed more for requests of very few features since all the features will be loaded into memory.

__Input__

  - session - a local instantiated BQSession attached to a MEX.
  - name - the name of the feature one wishes to extract
  - resource_list - list of the resources to extract. format: [(image_url, mask_url, gobject_url),...] if a parameter is not required just provided None

__Output__

  - return - a list of features as numpy array

> `length(session, name)`

Static method that returns the length of the feature requested.

__Input__

  - session - a local instantiated BQSession attached to a MEX.
  - name - the name of the feature one wishes to extract

__Output__

  - return feature length



## __Download an Array__ {-}

### Access an HDF5 Table from BisQue {-}

In this example, we will show you how to use the BQAPI to download a multidimensional array from within an HDF file and return it as a `numpy` array in `Python`.

***
The API call goes as follows:

1. Get the logger
1. Instantiate a BisQue session
1. Login using `USERNAME` and `PASSWORD`
1. Instantiate the `table` service
1. Use the table service to load the array
1. Return the array

***

#### Step 0. Import Dependencies {-}

Before we can even attempt anything cool with the API, we need to import the necessary packages. In this case, we need the following packages:

```python
import numpy as np
import logging

from bqapi.services import tables
from bqapi import BQSession
from bqapi.util import fetch_blob
from bqapi.comm import BQCommError
from bqapi.comm import BQSession
```

Place these at the top of your Jupyter notebook or `Python` script to ensure these run first. If you have not installed the BQAPI via pip, then  [install the BQAPI here.](#pip-install)

#### STEP 1. Get the Logger {-}

The logger service allows us to debug if anything goes wrong during the process of pulling our array. We use this in the BisQue core development as well, so feel free to gain greater insight into our other logger services as well.

We will define the `get_table` logger here.

```python
log = logging.getLogger('get_table')
```

#### STEP 2. Instantiate a BisQue session {-}

This instantiation enables the user to effectively communicate with BisQue. Without this, you will not be able to login and interact with the API.

```python
bq = BQSession()
```

#### STEP 3. Login using BisQue Credentials {-}

Here is where we will login into our BisQue account to access the data we have uploaded. We show an alternative chained version (line 2) of the commands here to instantiate the BQSession and login at the same time. 

```python
bq.init_local(user, pwd, bisque_root=root)
# bq = BQSession().init_local(user, pwd, bisque_root=root)
```

__Inputs__

If you do not have an account on BisQue, [make an account here](https://bisque.ece.ucsb.edu/registration//new).

- `USER` BisQue Username
- `PASSWORD` BisQue Password
- `bisque_root` "https://bisque.ece.ucsb.edu"

__Example.__
```python
bq.init_local(user=amil_khan, pass=bisque1234,
              bisque_root="https://bisque.ece.ucsb.edu")
```

#### STEP 4. Instantiate the `table` service {-}

Now we need to instantiate the table service. To do this, use _service_ to call the table service. Simple, right?

```python
table_service = bq.service ('table')
```

#### STEP 5. Using the Table Service {-}

In this example, we use the `load_array` function from the table service to return a `numpy` array from the respective HDF file on BisQue. What is most important is the input to this function, which is as follows:

```python
data_array = table_service.load_array(table_uniq, path, slices=[])
```

__Inputs__

- `table_uniq:` BisQue URI (__Required__)
- `path      :` Path to table within HDF  (__Required__)
- `slices    :` Slice of an array  (__Optional__)

__What is the `table_uniq`__ 

The `table_uniq` argument comes from how BisQue handles resources. Let's say you upload an image of a cat. BisQue will automatically assign a unique ID or, __URI__, to that image. Here is an example image:

```
https://bisque.ece.ucsb.edu/client_service/view?resource=https://bisque.ece.ucsb.edu/data_service/00-s5b358UmuziTaUqqYtTcPF
```

The last portion of the url is the URI. This is what you need to use as the input to the `table_uniq` argument.

```
https://bisque.ece.ucsb.edu/data_service/00-s5b358UmuziTaUqqYtTcPF
                                         ^-----------------------^
                                              COPY TABLE URI
```

__What is the `path`__ 

Say we have an array stored in a specific path in our HDF file. We can define a variable named `table_path` and place that after the `table_uniq` argument.

__Example__
```python
table_path = 'PATH/TO/ARRAY/IN/HDF'
table_service.load_array(uri, table_path)
```

#### Example. Functionalizing the Boring Stuff: `get_table`  {-}

Here we provide a full working example of how to functionalize the entire process. Overall, the structure is the same as the sum of its pieces, but now we can import many arrays into, say, our Jupyter Notebook for simple data processing tasks. You can also extend this example to upload the table back to BisQue once the data preprocessing is done.

```python
def get_table(user,pwd, table_PATH, uri=None,root='https://bisque.ece.ucsb.edu'):
    
    log = logging.getLogger('get_table')
    print("Starting Session...")
    
    bq = BQSession().init_local(user, pwd, bisque_root=root)
    print("BQSession Established. Attempting to fetch data...")
    
    table_service = bq.service ('table')
    print("Successfully Retrieved Array!")
    logging.basicConfig()

    
    return table_service.load_array(uri, table_PATH)
```

__Let's run our function!__

In this example, we are using the BQAPI to access an HDF file that contains a two-phase 3D microstructure.

```python
ms = get_table(amil_khan, bisque1234, 
              'DataContainers/ImageDataContainer/CellData/Phases',
              '00-orJQLiXgqh8K955C6qzhyC')
print('\nShape of table: {}'.format(ms.shape))
```
__`Output:`__
```
Starting Session...
BQSession Established. Attempting to fetch data...
Successfully Retrieved Array!

Shape of table: (5, 5, 5, 1)
```

## __Upload an Image__ {-}

In this example, we will show you how to use the BQAPI to upload one of the over 100+ supported Biological formats from a Jupyter Notebook.

***
The API call goes as follows:

1. Instantiate a BisQue session
1. Login using `USERNAME` and `PASSWORD`
1. Upload the Image

***

#### STEP 0. Import Dependencies {-}

Before we can even attempt anything cool with the API, we need to import the necessary packages. In this case, we need the following packages:

```python
import os
from bqapi.comm import BQSession
```

Place these at the top of your Jupyter notebook or `Python` script to ensure these run first. If you have not installed the BQAPI via pip, then  [install the BQAPI here.](#pip-install)

#### STEP 1. Instantiate a BisQue session {-}

This instantiation enables the user to effectively communicate with BisQue. Without this, you will not be able to login and interact with the API.

```python
bq = BQSession()
```

#### STEP 2. Login using BisQue Credentials {-}

Here is where we will login into our BisQue account to upload the data to our account. We show an alternative chained version (line 2) of the commands here to instantiate the BQSession and login at the same time. 

```python
bq.init_local(user, pwd, bisque_root=root)
# bq = BQSession().init_local(user, pwd, bisque_root=root)
```
__Inputs__

If you do not have an account on BisQue, [make an account here](https://bisque.ece.ucsb.edu/registration//new).

- `USER` BisQue Username
- `PASSWORD` BisQue Password
- `bisque_root` "https://bisque.ece.ucsb.edu"

__Example.__
```python
bq.init_local(user=amil_khan, pass=bisque1234,
              bisque_root="https://bisque.ece.ucsb.edu")
```

#### STEP 3. Upload the Image {-}

The final step is to upload the image on your local system to BisQue. To do this, we will use the instantiated session `bq` along with the `postblob` function to upload the `NIFTI` image below.
```python
# Post image to BisQue and get the response
image_path = '/PATH/TO/IMAGE/supercoolscientificimage.DICOM'
img_upload = bq.postblob(image_path) 
```
__Example.__
If your image is in the current directory of your Jupyter Notebook, then simply input the filename. Otherwise, specify the full path `/home/amil/Documents/T1_brain.nii.gz` or `~/Documents/T1_brain.nii.gz`.

```python
img_upload = bq.postblob('T1_brain.nii.gz') 
```

