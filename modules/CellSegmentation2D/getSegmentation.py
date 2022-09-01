import os
import logging
import argparse
import numpy as np
import matplotlib.pyplot as plt

import tifffile, json
from tqdm import tqdm
from scipy import ndimage as ndi
from skimage.io import imread
from skimage.color import rgb2gray
from skimage.transform import resize
from skimage.feature import peak_local_max
from skimage.measure import label, regionprops
from skimage.segmentation import find_boundaries, watershed
from skimage.morphology import h_minima, remove_small_objects

# logging.basicConfig(filename='PythonScript.log',filemode='a',level=logging.DEBUG)
# log = logging.getLogger('bq.modules')


def checkDir(dirPath):
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

# Adapted from https://stackoverflow.com/questions/17190649/how-to-obtain-a-gaussian-filter-in-python
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
    
def main(input_tiff, output_dir, area_thresh=500, plot_segment=False):
    checkDir(output_dir)

    ## DEFAULT VALUES ##
    img_gray = True
    thresh_jump = 0.005
    threshRange = np.arange(0.02, 0.08+thresh_jump,thresh_jump)
    # imgList = sorted(os.listdir(input_dir))

    ## Read metadata ##
    with tifffile.TiffFile(input_tiff) as tiff:
        imMeta = {}
        page = tiff.pages[0]
        tags = page.tags
        # import pdb; pdb.set_trace()
        for tag in tags:
            imMeta[tag.name] = tag.value
        # imMeta = json.dumps(imMeta)


    ## Read stack ##
    imgList = tifffile.imread(input_tiff)

    num_slices = imgList.shape[0]
    # outputFiles = []
    masks = []
    for idx, img_idx in enumerate(tqdm(range(num_slices), desc="Segmenting Slices")):
        threshMatrix = np.zeros((len(threshRange), 5))
        # print(idx)
        # img = imread(os.path.join(input_dir,imgPath),img_gray)

        img = resize(rgb2gray(imgList[img_idx].astype('uint8')), (512, 512))

        gBlurImg = ndi.convolve(img.astype(float), gauss2D(shape=(10, 10), sigma=15), mode='nearest')
   
        for idx_t, threshold in enumerate(threshRange):        
            labels, labels_bd = getWatershed(gBlurImg, threshold, area_thresh=500)
            regions = regionprops(labels)
            area = [region.area for region in regions]
            try:
                area_max_idx = np.argmax(area)
                area[np.argmax(area)] = 0
            except:
                area_max_idx = -1
                print("[INFO] No max area found")
                continue
            threshMatrix[idx_t, :] = [threshold, len(area), np.mean(area), np.std(area), area_max_idx]
        
        optThresh = getOptThreshold(threshMatrix)
        try:
            labels, labels_bd = getWatershed(gBlurImg, optThresh, area_thresh=500)
        except:
            print("[INFO] Unable to segment slice #{}. Generating empty mask.".format(idx))
            labels_bd = np.zeros_like(gBlurImg)

        masks.append(labels_bd)
        if plot_segment == True:
            fig, axes = plt.subplots(ncols=3, figsize=(9, 3), sharex=True, sharey=True)
            ax = axes.ravel()
            ax[0].imshow(img, cmap=plt.cm.gray, interpolation='nearest')
            ax[0].set_title('Original Image')
            ax[1].imshow(labels_bd, cmap=plt.cm.gray, interpolation='nearest')
            ax[1].set_title('Cell Boundary \n(optimal threshold:{})'.format(optThresh))
            ax[2].imshow(labels, cmap=plt.cm.gray, interpolation='nearest')
            ax[2].set_title('Instance Segmentation \n(optimal threshold:{})'.format(optThresh))

            for a in ax:
                a.set_axis_off()

            fig.tight_layout()
            f_name, f_ext = os.path.splitext(os.path.basename(imgPath))
            output_file_path = os.path.join(output_dir,f_name +'_seg' + f_ext)
            plt.savefig(output_file_path)
            # output_file = imread(output_file_path)
            # plt.show()
        # print('Optimal Threshold = {}'.format(optThresh))
        # outputFiles.append(output_file)


    filename = input_tiff.split('/')[-1].split('.')[0]
    outputFile = os.path.join(output_dir, filename + '_seg.tif')
    masks = np.expand_dims(np.array(masks).astype(np.uint16),0)
    tifffile.imsave(outputFile, masks, metadata=imMeta)

    return outputFile
            

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='UCR Watershed Segmentation')
    parser.add_argument('--input_dir', '-dir',  default='./example_data/input', type=str, help='directory path to input image')
    parser.add_argument('--output_dir', '-output_dir',  default='./example_data/segmented', type=str, help='directory path to store segmented image')
    parser.add_argument('--area_thresh', '-area', default=500,type=int, help='area threshold to remove small objects')
    parser.add_argument('--plot_segment', '-plot', action='store_true', help='plot segmentation while execution flag')

    args = parser.parse_args()
    #print(args)

    input_dir = args.input_dir
    output_dir = args.output_dir
    plot_segment = args.plot_segment
    area_thresh = args.area_thresh

    outputFiles = main(input_dir, output_dir, area_thresh, plot_segment)
    #print(np.array(outputFiles).shape)






        

        
