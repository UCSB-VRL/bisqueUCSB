#include <string.h>

#include "imageIO.h"
#include "cells.h"
#include "Args.h"
#include "tiffio.h"
#include <vector>

imageIO::imageIO(const string & file){
  filename.assign(file);
  img.image_stack = NULL;
  Error = false;
}

imageIO::~imageIO(){
  free(img.image_stack);
}

uchar * imageIO::loadImage(){
  if (Error){
    cerr << "Could not recover from previous error.\n";
    return NULL;
  }else if (! readImage()){
    cerr << "File not found.\n";
    Error = true;
    return NULL;
  }

  return img.image_stack;
}


int imageIO::readImage(){
  int index  = filename.find_last_of(".");
  int ret_val = 1;
  string ext;
  
  if (index == (int)string::npos){
    cerr << "Could not determine file type";
    return 0;
  }

  img.mag_factor = 1;
  img.xy_dist    = 1;
  img.z_dist     = 1;

  ext = filename.substr(index + 1);
  
  if (OPT_DEBUG > 0){
    cout << "Parsing " << ext << " file.\n";
  }

  if (ext == "PIC"){
    ret_val = readPic();
  }else if ((ext == "tif") || (ext == "TIF") || (ext == "tiff")){
    ret_val = readTiff();
  }else{
    ret_val = readCV();
  }

  if (fout.is_open()){
    fout << "*** Image Info ***" << endl
	 << "Width   : " << img.width << endl
	 << "Height  : " << img.height << endl
	 << "Depth   : " << img.depth << endl 
	 << "xy-plane in microns : " << img.xy_dist << endl
	 << "z-plane in microns  : " << img.z_dist << endl
	 << "z_ratio             : " << img.xy_dist / img.z_dist << endl
	 << "Magnification Factor: " << img.mag_factor 
	 << endl << endl;
  }

  if (OPT_DEBUG){
    cout << endl;
    cout << "Image Info: " << endl
	 << "Width : " << img.width << endl
	 << "Height: " << img.height << endl
	 << "Depth : " << img.depth << endl 
	 << "xy-plane in microns : " << img.xy_dist << endl
	 << "z-plane in microns  : " << img.z_dist << endl
	 << "Magnification Factor: " << img.mag_factor 
	 << endl << endl;
  }

  return ret_val;
}


int imageIO::readPic(){
  ushort file_id;
  int note_ptr = 0;
  short byte_format, dims[3];
  float m;
  char note[96] = {0};

  if (Error){
    cerr << "Could not recover from previous error.\n";
    return 0;
  }

  FILE * fin = fopen(filename.c_str(), "r");
  if (fin == NULL){
    cerr << "Error opening file.\n";
    Error = true;
    return 0;
  }

  if (fseek(fin, 0, SEEK_END) != 0){
    cerr << "Error...\n";
    Error = true;
    return 0;
  }

  // Move to check the file id, this tells us if this is
  // actually a BioRad file
  if (fseek(fin, 54, SEEK_SET) != 0){
    cerr << "Error ... \n";
    Error = true;
    return 0;
  }
  fread(&file_id, 1, sizeof(short), fin);
  if (file_id != 12345){
    cerr << "Not a valid BioRad file\n";
    Error = true;
    return 0;
  }

  // move back to the beginning of the file
  if (fseek(fin, 0, SEEK_SET) != 0){
    cerr << "Error...\n";
    Error = true;
    return 0;
  }

  // get dimensions of the data:
  // Image width, image height, size of z-series
  fread(&dims, 3, sizeof(short), fin);
  img.width  = dims[0];
  img.height = dims[1];
  img.depth  = dims[2];

  // Get the byte format of the file
  if (fseek(fin, 14, SEEK_SET) != 0){
    cerr << "Error...\n";
    Error = true;
    return 0;
  }
  fread(&byte_format, 1, sizeof(short), fin);
  if (byte_format != 1){
    cerr << "Invalid byte format!\n";
    Error = true;
    return 0;
  }

  // Get the magnification factor for this file
  if (fseek(fin, 66, SEEK_SET) != 0){
    cerr << "Error...\n";
    Error = true;
    return 0;
  }
  fread(&m, 1, sizeof(float), fin);
  img.mag_factor = m;


  if (fseek(fin, 10, SEEK_SET) != 0){
    cerr << "Error...\n";
    Error = true;
    return 0;
  }
  fread(&note_ptr, 3, sizeof(char), fin);

  img.image_stack = (uchar *) malloc(img.width * 
				     img.height * 
				     img.depth * sizeof(uchar));

  if (img.image_stack == NULL){
    cerr << "Could not allocate space for image stack...\n";
    Error = true;
    return 0;
  }

  if (fseek(fin, 76, SEEK_SET) != 0){
    cerr << "Error...\n";
    Error = true;
    return 0;
  }
  fread(img.image_stack, 
	(img.width * img.height * img.depth), 
	sizeof(uchar), fin);  

  if (note_ptr != 0){
    if (OPT_DEBUG) cout << "Parsing notes...\n";
    
    // there are notes at the end of the file!
    short tmp = 0;
    
    while (! feof(fin)){
      fread(note, sizeof(char), 96, fin);
      
      // read in note
      tmp = note[10];
      if (tmp == 20){
	// note type variable has been found.
	string block, val;

	block.assign(&note[16]);
	if (strncmp(block.c_str(), "AXIS_2", 6) == 0){
	  parseAxis(block, img.xy_dist);
	  //	}else if (strncmp(block.c_str(), "AXIS_3", 6) == 0){
	  //	  parseAxis(block, img.y_dist);
	}else if (strncmp(block.c_str(), "Z_CORRECT_FACTOR", 16) == 0){
	  val  = block.substr(19);
	  
	  img.z_dist = img.xy_dist / atof(val.c_str());
	}else if (strncmp(block.c_str(), "LENS_MAGNIFICATION", 18) == 0){
	  val  = block.substr(21);
	  
	  img.mag_factor = atof(val.c_str());
	}
      }
    }
  }  
  fclose(fin);

  return 1;
}

void imageIO::parseAxis(string & block, double & dist){
  const uint OFFSET = 9;
  string type, val;
  int idx1, idx2, t;

  idx1 = block.find(" ", OFFSET);
  type = block.substr(OFFSET, idx1 - OFFSET);
  
  t = atoi(type.c_str());

  if ((t & 0xf) != 1){
    cerr << "** Could not parse units. **" << endl;
  }
  
  idx1 = block.find(" ", idx1 + 1);
  idx2 = block.find(" ", idx1 + 1);
  val  = block.substr(idx1, idx2 - idx1);
  
  dist = atof(val.c_str());
}


/*
 * This seems like a horrible idea, but I couldn't find
 * any functions from the libtiff that would tell me
 * how many 'planes' are in a tiffDirectory
 */
int imageIO::getTiffCount(){
  int cnt = 0;
  TIFF * image;

  image = TIFFOpen(filename.c_str(), "r");

  if (image != NULL) {
    do {
      ++cnt;
    }while (TIFFReadDirectory(image));
  }else{
    cnt = -1;
  }
  
  (void) TIFFClose(image);

  return cnt;
}


// Can read in a multi-planar tiff file
int imageIO::readTiff(){
  TIFF * image;
  uint width, height, depth, planesize;
  uint offset = 0;
  int unit;

  // Open the TIFF image
  image = TIFFOpen(filename.c_str(), "r");

  // Find the width and height of the image
  TIFFGetField(image, TIFFTAG_IMAGEWIDTH, &width);
  TIFFGetField(image, TIFFTAG_IMAGELENGTH, &height);
  depth = getTiffCount();

  img.height = height;
  img.width  = width;
  img.depth  = depth;
  img.image_stack = (uchar *) malloc (height * width * depth * sizeof(uchar));

  if (img.image_stack == NULL){
    cerr << "Error, could not allocate enough memory for image stack.\n";
    return 0;
  }

  TIFFGetField(image, TIFFTAG_RESOLUTIONUNIT, &unit);
  TIFFGetField(image, TIFFTAG_XRESOLUTION, &img.xy_dist);

  if (unit == RESUNIT_CENTIMETER){
    /*
     * divide by 10,000 to convert from centimeters to microns
     * take inverse to get microns/pixel
     */
    img.xy_dist = (1 / (img.xy_dist / 10000));
  }else if (unit == RESUNIT_INCH){
    // divide by 24,500 to convert from inches to microns 
    img.xy_dist = (1 / (img.xy_dist / 25400));
  }
  
  planesize = height * width;

  if (image != NULL) {

    uint bufsize= TIFFStripSize(image);
    uchar * buf = (uchar *) _TIFFmalloc(bufsize);
    uint s, ns  = TIFFNumberOfStrips(image);
    uint *bytecounts;

    do {
      
      TIFFGetField(image, TIFFTAG_STRIPBYTECOUNTS, &bytecounts);
      for (s = 0; s < ns; s++) {
	
	// check to see if we need to resize the buffer
	if (bytecounts[s] != (uint)bufsize){
	  buf = (uchar *)_TIFFrealloc(buf, bytecounts[s]);
	  if (!buf){
	    return 0;
	  }
	  bufsize = bytecounts[s];
	}
	
	// try to read the strip
	if (TIFFReadRawStrip(image, s, buf, bytecounts[s]) < 0){
	  // if we encounter an error, free the buffer and return
	  _TIFFfree(buf);
	  return 0;
	}else{
	  memcpy(&img.image_stack[offset], buf, (bufsize * sizeof(uchar)));
	  offset += bufsize;
	}
      }
      
    } while (TIFFReadDirectory(image));
    _TIFFfree(buf);
  }

  /*
    // DEBUG
    tstrip_t strip;
    uint32* bc;
    
    TIFFGetField(image, TIFFTAG_STRIPBYTECOUNTS, &bc);

      
    int cnt = 0;


    do {
      cout << "strip byte counts: " << bc[cnt++] << endl;

      // Read the image into the memory buffer
      if(TIFFReadRGBAStrip(image, 0, raster) == 0){
	fprintf(stderr, "Could not read image\n");
	return 0;
      }

      for (i = 0; i < planesize; ++i){
	img.image_stack[offset + i] = ((uchar) TIFFGetR(raster[i]));
      }
      offset += planesize;

      cout << "raster[" << offset - 1 << "] = " << TIFFGetR(raster[offset - 1]) << endl;      
      printf("img[%i] = %i\n", offset - 1, img.image_stack[offset - 1]);

    } while (TIFFReadDirectory(image));

    free(raster);
    (void) TIFFClose(image);
  }
  */
  return 1;
}


int imageIO::readCV(){
  IplImage * cv_img = NULL;
  cv_img = cvLoadImage( filename.c_str() ); // load image

  if (cv_img == NULL){
    cerr << "File not found.\n";
    return 0;
  }
  uint i, size, channels = (uint)cv_img->nChannels;

  // copy info over to my imgStack format
  img.height = cv_img->height;
  img.width  = cv_img->width;
  img.depth  = 1;

  // not sure how to get this info?????????
  img.mag_factor = 1;
  img.xy_dist    = 1;
  img.z_dist     = 1;

  size = img.width * img.height * img.depth;
  img.image_stack = (uchar *) malloc(size * sizeof(uchar));

  for (i = 0; i < size; ++i){
    img.image_stack[i] = (uchar)cv_img->imageData[channels * i];
  }
  
  return 1;
}

void imageIO::getDimensions(uint & h, uint & w, uint & d){
  h = img.height;
  w = img.width;
  d = img.depth;
}

void imageIO::getScaleFactors(double & xy_plane, double & z_plane){
  xy_plane = img.xy_dist;
  z_plane  = img.z_dist;
}


void imageIO::writeImage(const float * steady_state, uint max_visits, pixel center) {
  //const uint Z_AREA = 1;
  const double block_size = (2 * AREA + 1) * (2 * AREA + 1);// * (Z_AREA * Z_AREA + 1);

  uint i, j;
  float block_mean = 0.0;
  float min_val    = 1.0 / max_visits;

  // Do thresholding
  if (OPT_THRESHOLD){

    // find the block of pixels aroung the center that we will use for thresholding
    for (i = (center.x - AREA); i <= (center.x + AREA); ++i) {
      for (j = (center.y - AREA); j <= (center.y + AREA); ++j) {
	//for (k = (center.z - Z_AREA); k <= (center.z + Z_AREA); ++k) {
	  pixel cur = {i, j, center.z};
	  block_mean += steady_state[OFFSET(img, cur)];
	  //}
      }      
    }
    
    block_mean /= block_size;

    if (fout.is_open()){
      fout << "Cell body size        : " << block_size << endl 
	   << "Mean cell body value  : " << block_mean << endl
	   << "Min threshold         : " << min_val << endl << endl;
    }
      
    if (OPT_DEBUG > 0){
      cout << "Cell body size      : " << block_size << endl 
	   << "Mean cell body value: " << block_mean << endl
	   << "Min threshold       : " << min_val << endl;
    }

    block_mean -= min_val;
  }else{
    block_mean = 1.0;
    min_val    = 0.0;
  }

  /*
   * ************** WRITE MULTI-PLANAR TIFF FILE **************
   */ 
  string outfile = OPT_IMAGEOUT + "stack.tif";
  TIFF * image;
  uint rowsperstrip, page;
  double norm;
  char page_number[20], z_depth[40];

  uchar * row = (uchar *) malloc(img.width * sizeof(uchar));
  
  // Open the TIFF file
  if((image = TIFFOpen(outfile.c_str(), "w")) == NULL){
    cerr << "Could not open " << outfile << " for writing\n";
  }
  
  // Loop through each plane of the image
  for (page = 0; page < img.depth; ++page){
      TIFFSetField(image, TIFFTAG_IMAGEWIDTH, img.width);
      TIFFSetField(image, TIFFTAG_IMAGELENGTH, img.height);
      TIFFSetField(image, TIFFTAG_IMAGEDEPTH, img.depth);      
      TIFFSetField(image, TIFFTAG_BITSPERSAMPLE, 8);
      TIFFSetField(image, TIFFTAG_SAMPLESPERPIXEL, 1);
      
      rowsperstrip = TIFFDefaultStripSize(image, -1);
      
      TIFFSetField(image, TIFFTAG_ROWSPERSTRIP, rowsperstrip);
      TIFFSetField(image, TIFFTAG_COMPRESSION, COMPRESSION_NONE);
      TIFFSetField(image, TIFFTAG_PHOTOMETRIC, PHOTOMETRIC_MINISBLACK);
      
      TIFFSetField(image, TIFFTAG_FILLORDER, FILLORDER_MSB2LSB);
      TIFFSetField(image, TIFFTAG_PLANARCONFIG, PLANARCONFIG_CONTIG);

      // set the resolution, we multiply by 10,000 to convert from
      // microns (10^-6) to centimerters (10^-2)
      TIFFSetField(image, TIFFTAG_RESOLUTIONUNIT, RESUNIT_CENTIMETER);
      sprintf(z_depth, "z_resolution: %f", (img.z_dist * 10000));
      TIFFSetField(image, TIFFTAG_XRESOLUTION, (img.xy_dist * 10000));
      TIFFSetField(image, TIFFTAG_YRESOLUTION, (img.xy_dist * 10000));
      // not sure where else to put the z_resolution data????
      TIFFSetField(image, TIFFTAG_ARTIST, z_depth);

      sprintf(page_number, "Page %d", page + 1);
      TIFFSetField(image, TIFFTAG_SUBFILETYPE, FILETYPE_PAGE);
      TIFFSetField(image, TIFFTAG_PAGENUMBER, page + 1, page + 1);
      TIFFSetField(image, TIFFTAG_PAGENAME, page_number);
   

      for (i = 0; i < img.height; ++i){
	
	// compute pixel values
	for (j = 0; j < img.width; ++j) {
	  norm = (fabs(steady_state[(page * img.height * img.width) + 
				    (img.width * i) + j] - min_val) / block_mean);
	  row[j] = (uchar)(min(1.0, norm) * 255);
	}
	
	// write a single row of the image
	if (TIFFWriteScanline(image, row, i, 0) == -1){ 
	  printf("Error!!\n");
	}
      }

      // write one plane of the image
      if (img.depth > 1){
	TIFFWriteDirectory(image);
      }
  }
  
  free(row);
  TIFFClose(image);
}

    
    
    
    
    
    
    
    
