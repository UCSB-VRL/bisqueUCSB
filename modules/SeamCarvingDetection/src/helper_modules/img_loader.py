import cv2    

def load_img(file):
    img = cv2.imread(file)
    if len(img.shape) == 3:
        img = cv2.imread(file)[:,:,[2,1,0]]
    return img
