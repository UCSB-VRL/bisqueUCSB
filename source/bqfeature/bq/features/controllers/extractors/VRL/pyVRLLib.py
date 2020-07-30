import numpy as np
import ctypes as ct
import inspect, os
import warnings
from bq.util.paths import run_path


#path=os.path.dirname(__file__) #find current dir of the file
#path = os.path.join(path,'..','..','..','..','src','extractors','VRL','lib')
#_VRLLib_warp= np.ctypeslib.load_library('_VRLLib', path)
_VRLLib_warp=None
def load_lib():
    global _VRLLib_warp
    if _VRLLib_warp is None:
        path = run_path ('bqfeature', 'bq', 'src','extractors', 'VRL','lib')
        _VRLLib_warp = np.ctypeslib.load_library('_VRLLib', path)
    return _VRLLib_warp


def extractEHD(im):
    """
    Edge Histogram Descriptor -

    @im   - a mxn numpy unit matrix (grayscale image matrix)

    @result - the resulting edge histogram descriptor with given length
    """
    load_lib()
    #EHD
    _VRLLib_warp.extractEHD.argtypes = [np.ctypeslib.ndpointer(dtype = np.intc), \
                                        ct.c_int, ct.c_int,\
                                        np.ctypeslib.ndpointer(dtype = np.double)]
    _VRLLib_warp.extractEHD.restype  = ct.c_void_p

     #check if the image is in the correct format
    tmp = np.asarray(im)
    if not len(tmp.shape)==2:
        raise TypeError("Requires a grayscale image")

    rows, cols = tmp.shape
    im = tmp.astype(np.intc)
    result = np.empty([80], dtype=np.double)
    _VRLLib_warp.extractEHD(im, rows, cols, result)
    return result


def extractHTD(im, mask = None):
    """
    Homogenious Texture Descriptor -

    @im   - a mxn numpy unit matrix (grayscale image matrix)

    @result - the resulting homogenious texture descriptor with given length
    """
    load_lib()

    #HTD
    _VRLLib_warp.extractHTD.argtypes = [np.ctypeslib.ndpointer(dtype = np.intc),\
                                        np.ctypeslib.ndpointer(dtype = np.intc),\
                                        np.ctypeslib.ndpointer(dtype = np.intc),\
                                        ct.c_int, ct.c_int, ct.c_int,\
                                        np.ctypeslib.ndpointer(dtype = np.double)]
    _VRLLib_warp.extractHTD.restype  = ct.c_void_p

    #check if the image is in the correct format
    tmp = np.asarray(im)
    if not len(tmp.shape)==2:
        raise TypeError("Requires a grayscale image")

    try:
        rows, cols = tmp.shape
    except ValueError:
        warnings.warn("Requires a grayscale numpy image", UserWarning)
        return

    #if not mask
    if mask == None:
        mask= np.zeros([rows,cols])

    if tmp.shape!=mask.shape:
        raise TypeError("The column and row vectors must be equal between")


    mask_labels = np.unique(mask)
    label_count = len(mask_labels)

    im = tmp.astype(np.intc)
    mask = mask.astype(np.intc)
    mask_labels = mask_labels.astype(np.intc) # pylint: disable=no-member
    result = np.empty([48*label_count], dtype=np.double)
    _VRLLib_warp.extractHTD(im, mask, mask_labels, label_count, rows, cols, result)
    result = np.reshape(result,(label_count,48))
    return result, mask_labels


if __name__=='__main__':
    from PIL import Image
    import time
    im = Image.open('test.jpg').convert("L")
    im = np.array(im)
    mask = Image.open('mask.gif')
    mask = np.array(mask)

    start=time.time()
    feature = extractEHD(im)
    #feature, label=extractHTD(im,mask=mask)
    end=time.time()
    print 'time elapsed: %s'%str(end-start)
    print feature
