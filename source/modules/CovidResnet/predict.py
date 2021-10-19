## 2D covid predictor

import torch
import SimpleITK as sitk
import cv2
from lungmask import mask
import SimpleITK as sitk
import numpy as np
from torchvision import models, transforms
from PIL import Image
import sys
import nibabel as nib
from bqapi import *

from bqapi.util import fetch_blob

import xml.etree.ElementTree as ET

import os

import logging
#constants
DATA_SERVICE                    = 'data_service'


#logging.basicConfig(level=logging.DEBUG)
##logging.basicConfig(filename='CovidResnet.log',filemode='a',level=logging.DEBUG)
##log = logging.getLogger('bq.modules')



import os, sys

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout



def transform(tmp):
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    transformer = transforms.Compose([
        transforms.Resize(224),
        transforms.ToTensor(),
        normalize
    ])


    return transformer(tmp)

def rescale_and_mask(log, image_path):

    with HiddenPrints():
        image_raw_arr=nib.load(image_path).get_fdata()
        image_comp_arr=np.zeros((image_raw_arr.shape[2],224,224))


        log.info('image depth: %s'% (image_raw_arr.shape[2]))
        for j in range(image_comp_arr.shape[0]):
            image_comp_arr[j]=cv2.resize(image_raw_arr[:,:,j],(224,224),interpolation = cv2.INTER_AREA)
#        image_comp = sitk.GetImageFromArray(image_comp_arr)

#        log.info('Get mask model')
#        model = mask.get_model('unet','R231CovidWeb')
#        log.info('Apply mask')
#        segmentation_mask = mask.apply(image_comp,model)
#        return [image_comp_arr, segmentation_mask]
        return image_comp_arr

def pre_process(log, image_path):

##    print(log, image_path)

#    image_arr, mask_arr = rescale_and_mask(log, image_path)
    
    # Masking

#    image_arr[mask_arr==0] = -2400

#    image_arr[image_arr<-1250] = -1250
#    image_arr[image_arr>250] = 250
#    image_arr = ( image_arr + 1250 ) / 1500

    image_arr = rescale_and_mask(log, image_path)


    return image_arr


def predict_label(log, image_name):

    image_path=image_name
    input_image = pre_process(log, image_path)
    model_input = torch.zeros(1,3,224,224)
    

    model_resnet = models.resnet152(pretrained=True)
    log.info('Model loaded')
    model_resnet.load_state_dict(torch.load('epoch30_ResNet152.pt',map_location='cpu'))
    log.info('Weights loaded')
    normal=0
    pna=0
    covid=0



    for i in range(input_image.shape[0]):
        tmp = (Image.fromarray(np.uint8((input_image[i,:,:])*255))).convert('RGB')
        tmp_t = transform(tmp)
        model_input[0,:,:,:] = tmp_t
        output = model_resnet(model_input)
        pred = output.argmax(dim=1, keepdim=True).numpy()
        pred = pred.tolist()
        if pred[0][0]==0:
            covid+=1
        elif pred[0][0]==1:
            pna+=1
        elif pred[0][0]==2:
            normal+=1
    return input_image.shape[0], covid, pna, normal

def predict_label_fake(log, image_name):
    return 100, 100, 0, 0

def main():


    if True:

        root='https://bisque.ece.ucsb.edu'
        user =sys.argv[1]

        pswd =sys.argv[2]

        image_url='https://bisque.ece.ucsb.edu/data_service/00-A9XmFnyReEWmGWU7NpwpA5'

        session = BQSession().init_local(user, pswd,  bisque_root=root, create_mex=False)

        logging.basicConfig(filename='test.log', encoding='utf-8', level=logging.DEBUG)
        image = session.load(image_url)
        print(image)

        folder='/module/source/'
        image_name=image.__dict__['name']

        print(image_name)
        result = fetch_blob(session, image_url, dest=folder+image_name)

        if '.gz' in image_name:
            os.rename(image_name,image_name.replace('.gz',''))
            image_name=image_name.replace('.gz','')
        z, covid, pna, normal = predict_label(logging, image_name)
        print(z, covid, pna, normal)

    else:
        print('Input image path')
        

        
if __name__ == "__main__":
        
    main()
    

    
