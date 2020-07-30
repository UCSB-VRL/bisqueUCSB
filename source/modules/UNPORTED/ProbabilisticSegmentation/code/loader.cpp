#include "loader.h"
#include <string.h>
#include "cells.h"
#include "Args.h"

loader::loader(const char * file){
  filename = (char *) malloc(strlen(file) * sizeof(char));

  if (filename == NULL){
    cerr << "Error allocating space for filename!\n";
    return;
  }

  strcpy(filename, file);
 
  MPI_Comm_size (MPI_COMM_WORLD, &nproc);
  MPI_Comm_rank (MPI_COMM_WORLD, &rank);
}

loader::~loader(){
  free(filename);
  cvReleaseImage( &img );
}


int loader::loadImage(){
  
  img = cvLoadImage( filename ); // load image

  if (img == NULL){
    cerr << "File not found.\n";
    return 0;
  }

  height = (*img).height;
  width  = (*img).width;

  return 1;
}


void loader::flatten3Channels(ushort * gray_scale, ushort & max){
  uint x, index;
  

  max = 0;
  
  // Color channels are in order of Blue, Green, Red
  for (x = 0 ; x < width*height; ++x){
    index = x;
    
    // combine the blue and green channels - ordered: BGR 
    gray_scale[index] = ((uchar)(*img).imageData[(x * 3)] + 
			 (uchar)(*img).imageData[(x * 3) + 1]);

    // track the maximum intensity value
    if (gray_scale[index] > max){
      max = gray_scale[index];
    }
  }
}

ushort * loader::flatten(){
  uint x, index;
  float temp_rows;
  
  ushort max = 0;
  ushort * gray_scale = NULL;

  height = (*img).height;
  width  = (*img).width;

  // determine how much of the image should go on this processor
  temp_rows = (float) rank * ((float) height / (float) nproc);
  
  start = (uint) temp_rows * (uint) width;
  temp_rows = (float) (rank + 1) * ((float) height / (float) nproc);
  stop  = (uint) temp_rows * (uint) width;
  if (rank == nproc - 1) stop = height * width;

  all_start = (uint *) malloc(nproc * sizeof(uint));
  all_stop  = (uint *) malloc(nproc * sizeof(uint));
  
  // all processes broadcast their start and stop points.  Useful later for reconstructing the image
  MPI_Allgather(&start, 1, MPI_UNSIGNED, all_start, 1, MPI_UNSIGNED, MPI_COMM_WORLD);
  MPI_Allgather(&stop,  1, MPI_UNSIGNED, all_stop,  1, MPI_UNSIGNED, MPI_COMM_WORLD);
  
  gray_scale = (ushort *) malloc((height * width) * sizeof(ushort));  

  
  if (gray_scale == NULL){
    cerr << "Insufficient memory for matrix!\n";
    return 0;
  }

  switch ((*img).nChannels){
    /*
     * We've probably been handed a grayscale image.
     * All we need to do here is find the maximum intensity value so we can normalize
     */
  case 1:

    // find the max intensity value
    for (x = 0; x < height*width; ++x){    
      index = x;
      gray_scale[index] = (*img).imageData[x];
      
      if (gray_scale[index] > max){
	max = gray_scale[index];
      }
    }
    
    break;
    /*
     * We've probably been handed a normal RGB image.
     * We need to condense the green and blue channels here and find the max
     * intensity value from this.
     */
  case 3:
    flatten3Channels(gray_scale, max);
    break;
  
  default:
    break;
  }
  

  /*
   * Normalize the image to the maximum intensity value
   */
  for (x = 0; x < height * width; ++x){
    gray_scale[x] = (ushort)(256 * ((double)gray_scale[x] / (double)max));
  }

  return gray_scale;
}


void loader::getDimensions(uint & h, uint & w){
  h = height;
  w = width;
}

void loader::getStartStop(uint & start_out, uint & stop_out){
  start_out = start;
  stop_out  = stop;
}

void loader::sendPartialImages(double * partialPVector) {
    int  i;
    int * displs, * proc_counts;

    if (rank == 0) {
      PVector = (double *) malloc(width*height*sizeof(double));
    }

    displs = (int *) malloc(nproc*sizeof(int));
    proc_counts = (int *) malloc(nproc*sizeof(int));

    for (i = 0; i < nproc; ++i) { 
      displs[i] = (int) all_start[i];
      proc_counts[i] = (int) all_stop[i] - all_start[i];
    } 
    
    // gather all the processors vectors in rank 0
    MPI_Gatherv(partialPVector, 
		(int) stop-start, 
		MPI_DOUBLE, PVector, 
		proc_counts, displs, 
		MPI_DOUBLE, 0, MPI_COMM_WORLD) ;
}

void loader::writeImage(pixel center) {
     CvSize size = cvSize(width, height);
     IplImage * segimg;
     const uint block_size = (2 * AREA + 1) * (2 * AREA + 1); 
     uint i, j;
     int * lin_block, indexi, indexj;
     pixel * cart_block;
     double block_mean = 0;
          
     // Do thresholding
     if (OPT_THRESHOLD) {
        // Space for cartesian coors and linear coors
        lin_block  = (int *) malloc(block_size * sizeof(int));
        cart_block = (pixel *) malloc(block_size * sizeof(pixel));
    
        // find the block of pixels aroung the center that we will use for thresholding
        for (i = (center.x - AREA); i <= (center.x + AREA); i++) {
            for (j = center.y - AREA; j <= center.y + AREA; j++) {
                indexi = i - (center.x - AREA);
                indexj = j - (center.y - AREA);
                cart_block[indexi*(2 * AREA + 1)+indexj].x = i;
                cart_block[indexi*(2 * AREA + 1)+indexj].y = j;
            }
        }
        
        // convert the cart2 coordinates to linear 
        cart2lin(cart_block, lin_block, block_size);
  
        // compute the average
        for (i = 0; i < block_size; i++) {
	  block_mean += PVector[lin_block[i]];
        }
        block_mean = block_mean / block_size;
        
     }else{
       block_mean = 1;
     }
     
     // create image
     segimg = cvCreateImage(size, IPL_DEPTH_8U, 1);
     
     // do threshold, assign data to openCV image
     // invert to black on white image
     for (i = 0; i < width * height; i++) {
       (*segimg).imageData[i] =  (uchar) (fabs((1 - min((double) 1, 
							PVector[i] / block_mean))) * 255);
     }
    
     cvSaveImage(OPT_IMAGEOUT.c_str(), segimg);
 }

void loader::normalize(double * partialPVector) {
    
  double * all_maxs;
  double max = 0;
  int i;
  
  all_maxs = (double *) malloc(nproc * sizeof(double));
  
  for (i = 0; i < (int) (stop - start); i++) { 
    if (partialPVector[i] > max) {
      max = partialPVector[i];
    }
  }
  
  MPI_Allgather(&max, 1, MPI_DOUBLE, all_maxs, 1, MPI_DOUBLE, MPI_COMM_WORLD);
  
  max = 0;
  
  for (i = 0; i < nproc; i++) {
    if (all_maxs[i] > max)
      max = all_maxs[i];
  }
  
  if (max == 0) {
    cerr << rank << ": Divide by zero in normalize\n";
    return;
  }
  
  for (i = 0; i < (int) (stop - start); i++) { 
    partialPVector[i] = fabs(partialPVector[i] / max);
  }
}

void loader::cart2lin(pixel * cart, int * lin, int size) {
  int i;
  
  for (i = 0; i < size; i++) {
    lin[i] = cart[i].y * width + cart[i].x;
  }
}
    
    
    
    
    
    
    
    
