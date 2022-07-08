def center_crop(X,out_size):
    """
    Function to extract a crop image of given size from the center of input    
    """
    if len(X.shape)==2: h,w = X.shape
    else: h,w,c = X.shape
    bt = int((h-out_size[0])/2)  # box top
    bb = bt + out_size[0]  # box bottom
    bl = int((w-out_size[1])/2)  # box left
    br = bl + out_size[1]  # box right
    return X[bt:bb,bl:br]