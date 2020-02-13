#ifndef LOADER_H
#define LOADER_H

#include <iostream>
//#include <stdlib.h>
#include "cv.h"      // include core library interface
#include "highgui.h" // include GUI library interface
#include <mpi.h>
#include "common.h"

using namespace std;

class loader{
 private:

  // opencv image struct 
  IplImage * img;
    
  char * filename;
  
  uint start, stop;
  uint height, width;
  int rank, nproc;

  uint * all_start, * all_stop;
  
  void flatten3Channels(ushort * gray_scale, ushort & max);

  double * PVector;

 public:
  
  loader(const char * file);
  ~loader();
  
  /* 
   * loads the image from a file
   * returns 0 on success, return 1 on failure
   */
  int loadImage();

  /*
   * Reduces image from 3 color channels to 1
   */
  ushort * flatten();

  void getDimensions(uint & height, uint & width);
  void getStartStop(uint & start, uint & stop);

  // Write out the partial Vector
  void sendPartialImages(double * partialPVector);

  void writeImage(pixel center);
  
  void normalize(double * partialPVector);
  
  void cart2lin(pixel * cart, int * lin, int size);

};


#endif
