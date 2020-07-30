from scipy.signal import convolve2d # pylint: disable=import-error
import numpy as np
from numpy import histogram

def histogram_of_oriented_gradients(im, bins=9):
    """

    """
    KERNEL = np.array([[-1.0,0.0,1.0],[-1.0,0.0,1.0],[-1.0,0.0,1.0]])

    imx = convolve2d( im, KERNEL, mode='same' )
    imy = convolve2d( im, np.transpose(KERNEL), mode='same' )

    mag = np.sqrt(imx**2+imy**2)
    ori = np.arctan(imy/imx)
    hog,edges = histogram(ori,bins=9,range=(-np.pi/2,np.pi/2),weights=mag)
    return hog


if __name__ == '__main__':
    import cv2
    import time
    im = cv2.imread('image2.tif', 0)
    start = time.time()
    htd = histogram_of_oriented_gradients(im)
    end = time.time()
    print htd
    print 'Time: %s'%(end-start)