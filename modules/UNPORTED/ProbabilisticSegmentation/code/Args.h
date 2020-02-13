#ifndef ARGS_H
#define ARGS_H

#include <string>
#include <fstream>

#include "common.h"

using namespace std;

/*
 * Turns on additional output from building 
 * the transition matrix and solving
 */
extern uint OPT_DEBUG;
/*
 * Turns on thresholding
 */
extern uint OPT_THRESHOLD;
/*
 * Defines which cell in the cells list to segment
 */
extern uint OPT_SEGCELL;
/*
 * Defines the input image file
 */
extern string OPT_IMAGEIN;
/*
 * Defines the output image file
 */
extern string OPT_IMAGEOUT;
/*
 * Defines a file containing the cell centers
 * for all cells in the image
 */
extern string OPT_CELLS;
/*
 * Defines the restart probability
 */
extern double OPT_RESTART;
/*
 * Defines the tolerance level
 * This is used for the linear solver
 * (higher tolerance = quicker run time + lower quality)
 */
extern double OPT_TOLERANCE;
/*
 * Defines whether or not to adjust the restart probability
 * when moving away from the cell.
 * This ONLY effects the case in which we move away from
 * the cell and are NOT moving closer to another cell
 * (ie. single cell images, raising restart as we move toward edge of image)
 */
extern uint OPT_NORMADJ_RESTART;



// Not a command line argument:
// For writing the summary file
extern ofstream fout;

#endif
