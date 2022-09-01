import os
import logging
import argparse
import numpy as np
import matplotlib.pyplot as plt

from bqapi.comm import BQCommError
from bqapi.comm import BQSession

from scipy import ndimage as ndi
from skimage.io import imread
from skimage.transform import resize
from skimage.feature import peak_local_max
from skimage.measure import label, regionprops
from skimage.segmentation import find_boundaries
from skimage.morphology import h_minima, watershed, remove_small_objects


logging.basicConfig(filename='PythonScript.log',filemode='a',level=logging.DEBUG)
log = logging.getLogger('bq.modules')


#Adapted from https://stackoverflow.com/questions/17190649/how-to-obtain-a-gaussian-filter-in-python
def gauss2D(shape=(10,10),sigma=0.5):
    """
    2D gaussian mask - should give the same result as MATLAB's
    fspecial('gaussian',[shape],[sigma])
    """
    m,n = [(ss-1.)/2. for ss in shape]
    y,x = np.ogrid[-m:m+1,-n:n+1]
    h = np.exp( -(x*x + y*y) / (2.*sigma*sigma)*1.0 )
    h[ h < np.finfo(h.dtype).eps*h.max() ] = 0
    sumh = h.sum()
    if sumh != 0:
        h /= sumh*1.0

    return h


def getWatershed(gBlurImg,threshold,area_thresh=500):
    hMinImg = h_minima(gBlurImg,threshold)
    distance = ndi.distance_transform_edt(hMinImg)
    local_maxi = peak_local_max(distance, indices=False,footprint=np.ones((3, 3)),labels=hMinImg)
    markers = ndi.label(local_maxi)[0]
    labels = watershed(gBlurImg, markers)
    labels = remove_small_objects(labels,min_size=area_thresh,connectivity=8)
    labels_bd = find_boundaries(labels)

    return labels, labels_bd


def getOptThreshold(thresholdMetrics):
    std_ = thresholdMetrics[:,3]
    bg = thresholdMetrics[:,4]
    try:
        optThreshVec = np.where(std_ == np.min(std_[np.where(bg<3.0)]))[0]
    except:
        optThreshVec = np.where(std_ == std_.min())
    
    optThresh = np.mean(thresholdMetrics[optThreshVec,0])

    return optThresh
    
def getSegment(bq,log,directory,area_thresh,plot_segment):
    ## DEFAULT VALUES ##
    img_gray = True
    thresh_jump = 0.005
    threshRange = np.arange(0.02,0.08+thresh_jump,thresh_jump)

    imgList = os.listdir(directory)
    threshArray = []

    for idx,imgPath in enumerate(imgList):
        threshMatrix = np.zeros((len(threshRange),5))

        img = imread(os.path.join(directory,imgPath),img_gray)
        gBlurImg = ndi.convolve(img.astype(float),gauss2D(shape=(10,10),sigma=15),mode='nearest')    
    
   
        for idx_t, threshold in enumerate(threshRange):        
            labels, labels_bd = getWatershed(gBlurImg,threshold,area_thresh=500)
            regions = regionprops(labels)
            area = [region.area for region in regions]
            area_max_idx = np.argmax(area)
            area[np.argmax(area)] =0
            threshMatrix[idx_t,:] = [threshold, len(area), np.mean(area), np.std(area), area_max_idx]
        
        
        optThresh = getOptThreshold(threshMatrix)
        labels, labels_bd = getWatershed(gBlurImg,optThresh,area_thresh=500)
    
        if plot_segment == True:
            fig, axes = plt.subplots(ncols=3, figsize=(9, 3), sharex=True, sharey=True)
            ax = axes.ravel()
            ax[0].imshow(img, cmap=plt.cm.gray, interpolation='nearest')
            ax[0].set_title('Original Image')
            ax[1].imshow(labels_bd, cmap=plt.cm.gray, interpolation='nearest')
            ax[1].set_title('Cell Boundary Image')
            ax[2].imshow(labels, cmap=plt.cm.gray, interpolation='nearest')
            ax[2].set_title('Instance Segmented Image')

            for a in ax:
                a.set_axis_off()

            fig.tight_layout()
            #plt.savefig('./
            plt.show()
             
        print('Optimal Threshold = {}'.format(optThresh))    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='UCR Watershed Segmentation')
    parser.add_argument('--directory', '-dir',  default='./data', type=str, help='path to image directory')
    parser.add_argument('--output', '-output',  default='./data_segmented', type=str, help='directory to store segmented image')
    parser.add_argument('--area_thresh', '-area', default=500,type=int, help='area threshold to remove small objects')
    parser.add_argument('--plot_segment', '-plot', action='store_true', help='plot segmentation while execution flag')

    args = parser.parse_args()
    print(args)

    directory = args.directory
    output = args.output
    plot_segment = args.plot_segment
    area_thresh = args.area_thresh

    main(directory,area_thresh,plot_segment)






        

        
