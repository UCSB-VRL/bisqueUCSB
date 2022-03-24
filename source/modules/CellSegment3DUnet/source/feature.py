import numpy as np
from scipy import ndimage
from scipy.ndimage import measurements
import SimpleITK as sitk
from skimage import segmentation
from skimage import io
import os
import pandas as pd



def adj_list_to_matrix(adj_list):
    n = len(adj_list)
    adj_matrix = np.zeros((n,n))
    np.fill_diagonal(adj_matrix,0)
    for i in range(1,n+1):
        for j in adj_list[i]:
            adj_matrix[i-1,j-1] = 1
    return adj_matrix

def compute_cell_adjacent_table(seg_img):
    #seg_img[seg_img==17]=15
    Adjacent_table={}
    all_labels = np.unique(seg_img)
    #print all_labels
    #all_labels = np.delete(all_labels,all_labels==0)
    for i in all_labels:
        if i != 0:
            index_list = []
            for j in all_labels:
                if j !=0:
                    draw_board = np.zeros(seg_img.shape)
                    if i!=j:
                        draw_board[seg_img==i]=1
                        draw_board[seg_img==j]=1
                        draw_board = ndimage.binary_dilation(draw_board).astype(draw_board.dtype)
                        _,num = measurements.label(draw_board)
                        if num==1:
                            index_list.append(j)
                tmp_dict={}
                tmp_dict[i]=index_list
                Adjacent_table.update(tmp_dict)
    return Adjacent_table

def compute_contact_points(seg_img,Adj_matrix):
    n = len(Adj_matrix)
    [slices,x,y] = seg_img.shape
    wall = np.zeros([x,y])
    for i in range(n):
        for j in range(n):
            if Adj_matrix[i,j]==1:
                draw_board = np.zeros([slices,x,y])
                draw_contact = np.zeros([x,y])
                for k in range(slices-1,-1,-1):
                    #fig = plt.figure()
                    draw_board1 = np.zeros([x,y])
                    draw_board2 = np.zeros([x,y])
                    draw_board1[seg_img[k]==i+1]=1
                    draw_board1 = ndimage.binary_dilation(draw_board1).astype(draw_board1.dtype)
                    draw_board2[seg_img[k]==j+1]=1
                    #fig.add_subplot(3,1,1)
                    #plt.imshow(draw_board1,cmap='gray')
                    #fig.add_subplot(3,1,2)
                    #plt.imshow(draw_board2,cmap='gray')
                    draw_board2 = ndimage.binary_dilation(draw_board2).astype(draw_board2.dtype)
                    draw_board[k,:,:] = np.logical_and(draw_board1==1,draw_board2==1)
                    draw_board[k,:,:] = draw_board[k,:,:]*1
                    #filename =  "adjacent_cell_bound/{}{}slice{}.png".format(i+1,j+1,k+1)
                    #io.imsave(filename,draw_board[k,:,:])
                    #print "cell {} and cell {} in slice {}".format(i+1,j+1,k+1)
                    #fig.add_subplot(3,1,3)
                    #plt.imshow(draw_board,cmap='gray')
                    #plt.show()
                    #_,num = measurements.label(draw_board)
                    #if num==1:
                    #    wall = segmentation.find_boundaries(draw_board,connectivity=1,mode="thick")
                    #    break
                bound_len = np.zeros(slices)
                for kk in range(slices):
                    bound_len[kk] =draw_board[kk,:,:].sum()
                #print bound_len
                for kk in range(slices-1,0,-1):
                    if kk < slices-1:
                        if bound_len[kk]>bound_len[kk+1] and bound_len[kk]>bound_len[kk-1]:
                            draw_contact_temp = draw_board[kk,:,:]
                            draw_contact = np.zeros(draw_board.shape)
                            for jj in range(len(draw_contact)):
                                draw_contact[jj] = draw_contact_temp
                            filename =  "data5_contact/{}{}slice{}.nii.gz".format(i+1,j+1,kk+1)
                            draw_contact_img = sitk.GetImageFromArray((draw_contact*255).astype('uint8'))
                            sitk.WriteImage(draw_contact_img,filename)
                            break
    return wall

def compute_conjunction_points(seg_img,Adj_list):
    #print "compute conjunction points"
    #seg_img[seg_img==17]=15
    [slices,x,y] = seg_img.shape
    n = len(Adj_list)
    plane = seg_img[len(seg_img)/2+1]
    final = np.zeros((x,y))
    for i in Adj_list.keys():
        A = i
        A_neighbors = Adj_list[A]
        for j in range(len(A_neighbors)):
            B = A_neighbors[j]
            B_neighbors = Adj_list[B]
            for k in range(len(B_neighbors)):
                C = B_neighbors[k]
                draw_board1 = np.zeros((x,y))
                draw_board2 = np.zeros((x,y))
                draw_board3 = np.zeros((x,y))
                draw_board = np.zeros((x,y))
                if C in A_neighbors:
                    draw_board1[plane==A]=1
                    draw_board2[plane==B]=1
                    draw_board3[plane==C]=1
                    draw_board1 = ndimage.binary_dilation(draw_board1,iterations=1).astype(draw_board1.dtype)
                    draw_board2 = ndimage.binary_dilation(draw_board2,iterations=1).astype(draw_board2.dtype)
                    draw_board3 = ndimage.binary_dilation(draw_board3,iterations=1).astype(draw_board3.dtype)
                    #print "cell {} {} {}".format(A,B,C)
                    #plt.imshow(draw_board1)
                    #plt.show()
                    draw_board =  np.logical_and(draw_board1==1,draw_board2==1)
                    draw_board = np.logical_and(draw_board==1,draw_board3==1)
                    final = np.logical_or(draw_board,final)
    final = final*1
    points = np.nonzero(final)
    return points

def cell_volumn(seg_img):
    print('Compute each cell volumn')
    all_labels = np.unique(seg_img)
    cell_volumn = []
    unique,counts = np.unique(seg_img,return_counts=True)
    return dict(zip(unique,counts))


# def f_1score(slice1,slice2):
#     eps = 0.000001
#     num = 2*(slice1*slice2).sum()
#     den = slice1.sum()+slice2.sum()
#     return num/den


# def seg_img_to_txt(path):
#     seg_img = sitk.ReadImage(path)
#     seg = sitk.GetArrayFromImage(seg_img)
#     i=0
#     for label in np.unique(seg):
#         i = i+1
#         if label != 0:
#             coordinate = np.argwhere(seg==label)
#             with open('/home/tom/cellfeat/coordinates/cell{}.txt'.format(i),'w') as f:
#                 for points in coordinates:
#                     print >>f,points

def main(path):
    files = os.listdir(path)
    for file in files:
        #print file
        seg_img = sitk.ReadImage(os.path.join(path,file))
        seg  = sitk.GetArrayFromImage(seg_img)
        #print seg.shape
        #plt.imshow(seg[0],cmap='gray')
        #plt.show()
        #pdb.set_trace()
        num_cells = len(np.unique(seg))-1
        #print num_cells
        #for label in np.unique(seg):
        adj_table = compute_cell_adjacent_table(seg)
        #print adj_table
        df = pd.DataFrame(adj_table)
        df.to_csv("result/adj_table.csv")
        points = compute_conjunction_points(seg,adj_table)
        #print points
        np.savetxt("result/points.csv", points, delimiter=",")
        #print cell_volumn(seg)
        df1 = pd.DataFrame(cell_volumn)
        df1.to_csv("result/cell_volumn.csv")
        #draw_board = np.zeros((512,512))
        #plt.imshow(seg[5],cmap='gray')
        #plt.plot(points[1],points[0],'r*')
        #plt.show()

#if __name__=='__main__':
 #   compute_features('result')