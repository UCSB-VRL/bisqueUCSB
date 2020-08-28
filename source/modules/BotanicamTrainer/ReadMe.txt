Botanicam Trainer ReadMe.txt

The module is a re-implementation of the Botanicam Trainer done in Matlab. It is an demo of a python module using bisque's feature service and python api (bqapi). This module is meant to be run by the admin in creating model files for the Botanicam module to classify image of plants. If the model for the Botanicam needs to be updated the admin can run this module with a chosen image set along with tags to train classes on the images. The Botanicam module will only pick up the last model file added to the system. If the admin wants to revert the model to an older one, delete the newest made models from the system or make them private so the Botanicam module cannot see the model files.


Requirements:
	The Botanicam Trainer module requires a few python libraries as well as the python bqapi. (Note: for windows you can use http://www.lfd.uci.edu/~gohlke/pythonlibs/ to download and install all of these libraries except bqapi)
	
	bqapi - comes with the bisque source
	scikit-learn - pip install (http://scikit-learn.org)
	scipy - pip install (http://www.scipy.org/)
	numpy - pip install (http://www.numpy.org/)
	numexpr - pip install (https://pypi.python.org/pypi/numexpr)
	pytables -  pip install (http://www.pytables.org/moin)
		also requires: libhdf5 (http://www.hdfgroup.org/HDF5/) debian use apt-get