import numpy as np

def FFTSD(contour,sample):
    """
        Fourier Shape Descriptor
    """
    int_index=[0]
    total_length = 0
    for i,con in enumerate(contour):
        if len(contour)-2>=i:
            total_length += np.sqrt((contour[i][1]-contour[i+1][1])**2+(contour[i][0]-contour[i+1][0])**2)
            int_index.append(total_length)

    X=[i[0] for i in contour]
    InterpX = np.interp(np.arange(0,total_length,total_length/float(sample)),int_index,X)
    Y=[i[1] for i in contour]
    InterpY = np.interp(np.arange(0,total_length,total_length/float(sample)),int_index,Y)
    z = [InterpX[i]+1j*InterpY[i] for i in xrange(len(InterpX))]
    fft_coeff = np.fft.fft(z)
    return [np.sqrt(i.imag**2+i.real**2) for count,i in enumerate(fft_coeff)]


#test code
if __name__=='__main__':
    import cv2
    import numpy as np
    import matplotlib.pyplot as plt  # pylint: disable=import-error
    im=cv2.imread('test.jpg',cv2.CV_LOAD_IMAGE_GRAYSCALE)
    ret,thresh = cv2.threshold(im,200,255,0)
    cv2.imwrite('thres_test.jpg',thresh)
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    len_max=0
    for i,con in enumerate(contours):
        if len(con)>len_max:
            index = i
            len_max=len(con)

    contours = contours[index]
    sample = 120
    mag_coeff = FFTSD(contours,sample)

    #sampling
    fig = plt.figure()
    a=[[count,i] for count,i in enumerate(mag_coeff) if count>0]
    plt.plot(*zip(*a), marker='*', color='r', ls='')
    plt.show()
