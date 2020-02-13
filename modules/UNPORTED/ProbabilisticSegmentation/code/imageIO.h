#ifndef IMAGEIO_H
#define IMAGEIO_H

#include <iostream>
#include <string>
#include "cv.h"      // include core library interface
#include "highgui.h" // include GUI library interface
#include "common.h"
#include "tiffio.h"

using namespace std;

class imageIO{
 private:
  bool Error;
  string filename;
  imgStack img;

  int readPic();
  int readCV();
  int readImage();
  int readTiff();

  void parseAxis(string & block, double & dist);
  int getTiffCount();

 public:
  
  imageIO(const string & file);
  ~imageIO();
  
  /* 
   * loads the image from a file
   * returns image pointer on success, NULL on failure
   */
  uchar * loadImage();
  imgStack * getImage(){ return &img; };

  // Get functions
  void getDimensions(uint & height, uint & width, uint & depth);
  void getScaleFactors(double & xy_plane, double & z_plane);

  // Write out the partial Vector
  void writeImage(const float * steady_state, uint max_visits, pixel center);
};

#endif
 
