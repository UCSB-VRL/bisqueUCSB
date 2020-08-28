#ifndef COMMON_H
#define COMMON_H

#include <cmath>
#include <string>

using namespace std;

typedef unsigned long long ullong; // 1.84e19
typedef unsigned long ulong;       // 4.29e9
typedef unsigned int uint;         // 4.29e9
typedef unsigned short ushort;     // 6.55e4
typedef unsigned char uchar;       // 2.55e2


#define OFFSET( img, p ) ((((img).width * (img).height) * (p.z)) + ((img).width * (p.y)) + (p.x))

/*
 * Governs how fast we increase the restart value as
 * we move further away from the current cell
 * (while not closer to any other cell)
 */
const double EXP = 4.0;

/*
 * This constant is used to scale the increase of the restart
 * value depending on how far a pixel is from the closest cell
 * and the current cell
 */
const uint MAX_DIST = 2000;

/*
 * Defines the number of neighbors a pixel has
 * (including itself)
 * 3 3x3 blocks = 9*3 = 27 
 */
const uint BLOCK = 27;
/*
 * Defines the area around the restart pixel to not
 * allow a pixel to restart.
 * This value also dictates how close you may walk to another
 * cell center before setting your restart value to 1
 */
const uint AREA  = 10;

/*
 * Total number of nonzero elements per column
 * in the transition matrix, including the restart 
 * row
 */
const uint COL_NNZ = BLOCK + 1;

// ================== Helper Structs ================
/*
 * Row Reduced Matrix format
 */
struct rrM{
  double * value;

  uint * x_ind;
  uint * y_ind;
};

struct hypreMatrix{
  int row_cnt, col_cnt, val_cnt;
  int nrows;
  int * ncols;
  
  int * rows;
  int * cols;
 
  double * values;
};

struct hypreCol{
  double values[COL_NNZ];

  int rows[COL_NNZ];
  int col; 
};

struct pixel{
  int x;
  int y;
  int z;
};

struct imgStruct{
  ushort * image;
  uint height;
  uint width;
};

struct imgStack{
  uchar * image_stack;  
  uint height;
  uint width;
  uint depth;

  // labels the number of microns per pixels
  double xy_dist, z_dist;
  // lens magnification
  double mag_factor;
};

typedef struct hypreMatrix hypreMatrix;
typedef struct imgStack imgStack;
typedef struct imgStruct imgStruct;
typedef struct rrM rrM;
typedef struct hypreCol hypreCol;
typedef struct pixel pixel;



#endif
