import numpy as np
#import numexpr as ne
#from scipy.signal import convolve2d,fftconvolve
#from multiprocessing import Pool


def gabor_gen(height,width,s,n,scales=4,orientations=6,Ul=0.05,Uh=.5):

    base = Uh/Ul
    a = base**(1.0/(scales-1))
    u0 = Uh
    sigmaU = ((a-1)*Uh)/((a+1)*np.sqrt(2*np.log(2)))
    z = -2*np.log(2)*sigmaU*sigmaU/Uh
    sigmaV = np.tan(np.pi/(2*orientations))*(Uh+z)/np.sqrt(2*np.log(2)-z*z/(sigmaU*sigmaU));
    sigmaY = 1/(2*np.pi*sigmaV);
    sigmaX = 1/(2*np.pi*sigmaU);
    coef = 1/(2*np.pi*sigmaX*sigmaY);
    t1 = np.cos(np.pi/orientations*n);
    t2 = np.sin(np.pi/orientations*n);

    x = np.linspace(0, width-1, width) - width/2 #width
    y = np.linspace(0, height-1, height) - height/2 #height
    xv,yv = np.meshgrid(x,y)

    X = (a**(-s))*(t1*xv+t2*yv)
    Y = (a**(-s))*(t1*yv-t2*xv)
    G = coef*(a**(-s))*np.exp(-.5*((X*X)/(sigmaX*sigmaX)+(Y*Y)/(sigmaY*sigmaY)))

    angle = 2*np.pi*u0*X
    gabor = G*np.sin(angle)

    return gabor


def homogenious_texture_descriptor(im, scales=4, orientations=6):

    HTDmean = []
    HTDstd = []
    for s in np.arange(0,scales):
        for o in np.arange(0,orientations):
            gabor = gabor_gen(im.shape[0],im.shape[1],s,o,scales,orientations)
            result = np.fft.irfft2(np.fft.rfft2(gabor) * np.fft.rfft2(im, gabor.shape)) #faster
            #result = np.fft.ifft2(np.fft.fft2(gabor) * np.fft.fft2(im, gabor.shape))
            result = np.absolute(result)
            HTDmean.append(np.mean(result))
            HTDstd.append(np.std(result))

    return HTDmean+HTDstd


if __name__ == '__main__':
    # import cv2
    # #import matplotlib.pyplot as plt
    # import time
    # im = cv2.imread('image2.tif',0)
    # start = time.time()
    # htd = Homogenious_Texture_Descriptor(im)
    # end = time.time()
    # print htd
    # print 'Time: %s'%(end-start)
    pass