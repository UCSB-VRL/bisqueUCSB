#include "Tmatrix.h"
#include "cells.h"
#include "Args.h"
// --------- Momentum Constants ----------
const double line  = 50.0;
const double same  = 1.0;
const double perp  = 0.0;
const double acute = 0.0010;
const double obt   = 0.0010;


const double 
Tmatrix::move_mask[][BLOCK] = {{line, acute, perp, acute, same, obt, perp, obt,line},
			       {acute, line, acute, perp, same, perp, obt, line, obt},
			       {perp, acute, line, obt, same, acute, line, obt, perp},
			       {acute, perp, obt, line, same, line, acute, perp, obt},
			       {same, same, same, same, same, same, same, same, same},
			       {obt, perp, acute, line, same, line, obt, perp, acute},
			       {perp, obt, line, acute, same, obt, line, acute, perp},
			       {obt, line, obt, perp, same, perp, acute, line, acute},
			       {line, obt, perp, obt, same, acute, perp, acute,line}};

const uint 
Tmatrix::come_from[] = {8, 7, 6, 5, 4, 3, 2, 1, 0};  


Tmatrix::Tmatrix(ushort * image_in, uint height_in, uint width_in, 
                 uint start_in, uint stop_in, uint rank_in, uint nproc_in) {

  uint i;
  uint hypre_nrows;
  uint * hypre_ncols;
  int * hypre_rows;
  int * hypre_cols;
  double * hypre_values;

  nnz = 0;
  img.height = height_in;
  img.width  = width_in;
  img.image  = image_in; // memcpy?
  
  img_cells = NULL;
  t.rows[COL_NNZ - 1] = 0;
  
  start = start_in;
  stop  = stop_in;
  rank  = rank_in;
  nproc = nproc_in;

  // hypre start/stop.  
  // Need to shift everything over by rank since we are 
  // adding extra rows/cols for the local restart
  hypre_start = (start + rank) * 9;
  hypre_stop  = (stop + rank + 1) * 9 - 1;

  HYPRE_IJMatrixCreate(MPI_COMM_WORLD, hypre_start, hypre_stop, hypre_start, hypre_stop, &A);
  HYPRE_IJMatrixSetObjectType(A, HYPRE_PARCSR);
  HYPRE_IJMatrixInitialize(A);

  hypre_nrows  = hypre_stop - hypre_start + 1;
  hypre_ncols  = (uint *) malloc(hypre_nrows * sizeof(uint));
  hypre_rows   = (int *) malloc(hypre_nrows * sizeof(int));
  hypre_cols   = (int *) malloc(hypre_nrows * sizeof(int));
  hypre_values = (double *) malloc(hypre_nrows * sizeof(double));
  
  if (OPT_DEBUG){
    cout << "Processor: " << rank
	 << " is processing " << hypre_nrows << " rows\n";
  }

  for (i = 0; i < hypre_nrows; i++) {
    hypre_ncols[i]  = 1;
    hypre_rows[i]   = hypre_start + i;
    hypre_cols[i]   = hypre_start + i;
    hypre_values[i] = 0;
  }
  
  // set values in hypre matrix
  HYPRE_IJMatrixAddToValues(A, hypre_nrows, 
                            (int *) hypre_ncols, 
			    (const int *) hypre_rows, 
			    (const int *) hypre_cols, 
			    (const double *) hypre_values);

  free(hypre_ncols);
  free(hypre_rows);
  free(hypre_cols);
  free(hypre_values);
}

void Tmatrix::addCells(pixel * centers_in, uint cell_count, double restart, int segcell){
  img_cells = new cells(centers_in, cell_count, restart, (uint) segcell);
}

/*
 * Neighbor array:  [ 0 3 6
 *                    1 4 7 
 *                    2 5 8 ]
 * If neighbors[] element is < 0, then no neighbor exists in that position
 * (ie. for edges of the image)
 */
void Tmatrix::getNeighbors(pixel in, pixel neighbors[]){
  uint i;
    
  // init the neighbors array
  for (i = 0; i < BLOCK; ++i){
    neighbors[i].x = -1;
    neighbors[i].y = -1;
  }

  // center position
  neighbors[4].x = in.x;
  neighbors[4].y = in.y;


  if (in.x > 0){

    // left edge
    neighbors[1].x = in.x - 1;
    neighbors[1].y = in.y;

    if (in.y > 0){
      // top left corner
      neighbors[0].x = in.x - 1;
      neighbors[0].y = in.y - 1;
    }

    if ((uint)in.y < (img.height - 1)){
      // bottom left corner
      neighbors[2].x = in.x - 1;
      neighbors[2].y = in.y + 1;
    }
  }

  if ((uint)in.x < (img.width - 1)){
    // right edge
    neighbors[7].x = in.x + 1;
    neighbors[7].y = in.y;

    if (in.y > 0){
      // top right corner
      neighbors[6].x = in.x + 1;
      neighbors[6].y = in.y - 1;
    }

    if ((uint)in.y < (img.height - 1)){
      // bottom right corner
      neighbors[8].x = in.x + 1;
      neighbors[8].y = in.y + 1;
    }
  }

  if (in.y > 0){
    // top edge
    neighbors[3].x = in.x;
    neighbors[3].y = in.y - 1;
  }    

  if ((uint)in.y < (img.height - 1)){
    // bottom edge
    neighbors[5].x = in.x;
    neighbors[5].y = in.y + 1;
  }

  // Calculate Transition matrix indices
  for (i = 0; i < BLOCK; ++i){
    if ((neighbors[i].x >= 0) && (neighbors[i].y >= 0)){
      t.rows[i] = (img.width * neighbors[i].y + neighbors[i].x) * 9 + come_from[i];
    }
  }
  t.col = 9 * (in.y * img.width) + (9 * in.x);
}


/*
 * Calculates the total pixel intensities summed over the whole block
 */
uint Tmatrix::blockIntensity(pixel in, pixel neighbors[], double probs[]){
  uint total = 0;
  uint i, offset;

  for (i = 0; i < BLOCK; ++i){
    
    if ((neighbors[i].x >= 0) && (neighbors[i].y >= 0)){
      offset = neighbors[i].y * img.width + neighbors[i].x;
      total += img.image[offset];
      probs[i] = img.image[offset];
    }
  }
  
  getProbabilities(total, neighbors, probs);

  return total;
}


/*
 * Calculates the probability of each pixel in a 3x3 block
 * given the total intensity summed over the block and the 
 * individual pixel values
 */
void Tmatrix::getProbabilities(uint total, pixel neighbors[], double probs[]){
  uint i;

  for (i = 0; i < BLOCK; ++i){

    if ((neighbors[i].x >= 0) && (neighbors[i].y >= 0)){
      probs[i] /= (double)total;
    }else{
      probs[i] = 0;
    }

  }
}

void Tmatrix::calcPixel(pixel index, pixel neighbors[], double probs[]){

  uint j, i = 0;

  // distances of all 'other' cells to a pixel index
  //double * dist_from_cells = img_cells->distFromCells(index);
  
  // current cell position
  pixel s = img_cells->getThisCell();
  
  while (i < BLOCK){
    
    // No neighbor in this position, so skip
    if ((neighbors[i].x < 0) || (neighbors[i].y < 0)){
      
      ++i;
      ++t.col;
      continue;
    }
    
    if (((index.x == 0) || ((uint)index.x == (img.width - 1))) || 
	((index.y == 0) || ((uint)index.y == (img.height - 1))) ||
	img_cells->insideMyCell(index)){
      // We are on an edge, or we're already in our own cell
      // center, so don't apply momentum

      for (j = 0; j < BLOCK; ++j){
	t.values[j] = probs[j];
      }
    }else{
      // Apply the momentum
      for (j = 0; j < BLOCK; ++j){
	t.values[j] = probs[j] * move_mask[i][j];
      }
    }
    
    t.values[COL_NNZ - 1] = img_cells->adjustRestart(index, t.values, img);
    reNormalize();

    setPixel(t);
    ++t.col;
    ++i;
  }
}


void Tmatrix::reNormalize(){
  uint i;
  double total = 0.0;
  double c_new;
  
  for (i = 0; i < BLOCK; ++i){
    total += t.values[i];
  }
  
  c_new = total * t.values[COL_NNZ - 1];
    
  if ((total + c_new) > 0){
    for (i = 0; i < BLOCK; ++i){
      t.values[i] /= (total + c_new);
    }
  }
}

int Tmatrix::Build(){
  uint i, j;
  uint total;
  pixel index;
  
  pixel neighbors[BLOCK];
  double probs[BLOCK];
  
  if (img_cells == NULL){
    cerr << "Initialize cells before building matrix. Quitting without building matrix.\n";
    return 0; 
  } 
  
  // loop through the image
  
  for (i = start; i < stop; ++i){
    index.x = i % img.width;
    index.y = i / img.width;

    // initialize hypre column structure
    t.col = 0;
    for (j = 0; j < BLOCK; ++j){
      t.rows[j] = -1;
      t.values[j] = 0;
    }

    getNeighbors(index, neighbors);
    total = blockIntensity(index, neighbors, probs);
    
    if (total > 0){
      calcPixel(index, neighbors, probs);
    }
  }

  if (OPT_DEBUG){
    cout << "Rank: " << rank << " is done setting " << nnz << " nonzero elements\n";
  }

  setRestart();
  initVectors();
  finalize();

  return 1;
}

// numrows = should be 10 always (9 pixels + 1 restart).  rows not being used have -1
// numcols = number of cols being set, should be 1
// cols, rows = indices to set.  cols should be of length 1, rows should be of length numrows.  Rows not being used
// have a -1 in their entry.  Cols should never have -1
// values = values to set, should be of length numrows.  This assumes that positions that are -1 still
// have an entry in values, it is not lookied at however
// 
// all values are PRE local restart shifting.  this function will take care of offsetting indices
// for local restart values
//
// restart is always the last one

void Tmatrix::setPixel(hypreCol tpixel) {

  uint nrows = COL_NNZ;
  //  uint ncols = 1;
  int * rows = tpixel.rows;
  int * cols = &(tpixel.col);
  double * values = tpixel.values;
  
  uint i;
  uint hypre_nrows = 0;
  uint * hypre_ncols;
  int * hypre_rows;
  int * hypre_cols;
  double * hypre_values;
  
  hypre_ncols = (uint *) malloc(nrows * sizeof(uint));
  hypre_rows = (int *) malloc(nrows * sizeof(int));
  hypre_cols = (int *) malloc(nrows * sizeof(int));
  hypre_values = (double *) malloc(nrows * sizeof(double));
  
        
  // only go to 9, since last one is restart
  for (i = 0; i < nrows - 1; i++) {

    if (rows[i] >= 0) {
      hypre_ncols[hypre_nrows] = 1;
      
      // adjust the rows.  
      if ((uint)rows[i] < (start * 9)){
	hypre_rows[hypre_nrows] = rows[i] + (rank - 1) * 9;
      }else if ((uint) rows[i] >= (stop * 9)){
	hypre_rows[hypre_nrows] = rows[i] + (rank + 1) * 9;
      }else{
	hypre_rows[hypre_nrows] = rows[i] + rank * 9;
      }

      // adjust columns by your rank...only ever set columsn in each processors area, so only
      // need to adjust cols by the number of addition cols before it (rank * 9)
      hypre_cols[hypre_nrows] = *cols + (rank * 9);
      hypre_values[hypre_nrows] = values[i];
      hypre_nrows++;
    }
  }
  
  // add local restart, ignoring the indices for the global restart
  // always know where to calculate it.  Local restart is always last row of this local portion 
  // of the matrix.  the column is the same.
  hypre_ncols[hypre_nrows] = 1;
  
  // stop row is the middle row of the extra 9 added (like the matlab code)
  // first = (9 * (x - 1) * height +  (y - 1) * 9) + 1;
  // s = first+4;%:(first + 8);
  hypre_rows[hypre_nrows] = hypre_stop - 4;
  hypre_cols[hypre_nrows] = *cols + (rank * 9);
  hypre_values[hypre_nrows] = values[nrows-1];

  hypre_nrows++;

  nnz += hypre_nrows;
  // set values in hypre matrix
  HYPRE_IJMatrixSetValues(A, hypre_nrows, 
			  (int *) hypre_ncols, 
			  (const int *) hypre_rows, 
			  (const int *) hypre_cols, hypre_values);
  
  free(hypre_ncols);
  free(hypre_rows);
  free(hypre_cols);
  free(hypre_values);
}



// set the restart row in the matrix.  Can be called collectively but only the processor with the restart row in it
// will actually set the values.
void Tmatrix::setRestart() {
    
  pixel center;
  int position, i;
  int proc_start, proc_stop;
  
  uint hypre_nrows = 1;
  int hypre_ncols = nproc;
  int hypre_rows;
  int * hypre_cols;
  double * hypre_values;
  
  
  
  center = img_cells->getThisCell();
  //center.x = 1;
  //center.y = 2;
  position = center.x + center.y * img.width;
  
  // this processor has the restart row
  if (position >= (int) start && position < (int) stop) {
    
    hypre_cols = (int *) malloc(nproc * sizeof(int));
    hypre_values = (double *) malloc(nproc * sizeof(double));
    
    hypre_rows = (position+rank) * 9 + 4;
    
    for (i=0; i< (int) nproc; i++) {
      
      proc_start = i * ((img.height * img.width) / nproc);
      proc_stop  = (i + 1) * ((img.height * img.width) / nproc);
      if (i == (int) nproc - 1) proc_stop = img.height * img.width;
            
      hypre_cols[i] = (proc_stop + i) * 9 + 4;
      hypre_values[i] = 1;
      
      if (OPT_DEBUG > 1){
	cout << "Global Restart added to row " << hypre_rows 
	     << " and column " << hypre_cols[i] << endl;
      }
      
    }
    
    HYPRE_IJMatrixSetValues(A, hypre_nrows, &hypre_ncols, (const int *) &hypre_rows, (const int *) hypre_cols, hypre_values);
    
    free(hypre_cols);
    free(hypre_values);
  }
}

void Tmatrix::initVectors() {

  double *rhs_values, *x_values;
  int    *rows;
  int local_size, i, position, restart_row;
  pixel center;
  
  HYPRE_IJVectorCreate(MPI_COMM_WORLD, hypre_start, hypre_stop,&b);
  HYPRE_IJVectorSetObjectType(b, HYPRE_PARCSR);
  HYPRE_IJVectorInitialize(b);
  
  HYPRE_IJVectorCreate(MPI_COMM_WORLD, hypre_start, hypre_stop,&x);
  HYPRE_IJVectorSetObjectType(x, HYPRE_PARCSR);
  HYPRE_IJVectorInitialize(x);
  
  local_size = (int) (hypre_stop - hypre_start) + 1;
  
  rhs_values = (double *) calloc(local_size, sizeof(double));
  x_values = (double *) calloc(local_size, sizeof(double));
  rows = (int *) calloc(local_size, sizeof(int));
  
  for (i = 0; i < local_size; i++){
    x_values[i] = 0.0;
    rows[i]     = hypre_start + i;
  }
  
  center = img_cells->getThisCell();
  //center.x = 1;
  //center.y = 2;
  
  position = center.x + center.y * img.width;
  
  // this processor has the restart row
  if (position >= (int) start && position < (int) stop) {
    restart_row = ((position+rank) * 9 + 4) - hypre_start;
    rhs_values[restart_row] = -1;
  }
  
  HYPRE_IJVectorSetValues(b, local_size, rows, rhs_values);
  HYPRE_IJVectorSetValues(x, local_size, rows, x_values);
  
  
  free(x_values);
  free(rhs_values);
  free(rows);
}

void Tmatrix::finalize() {
    
    uint i;
    uint hypre_nrows = (hypre_stop-hypre_start) + 1;
    uint * hypre_ncols;
    int * hypre_rows;
    int * hypre_cols;
    double * hypre_values;
    
    
    HYPRE_IJVectorAssemble(b);
    HYPRE_IJVectorGetObject(b, (void **) &par_b);
  
    HYPRE_IJVectorAssemble(x);
    HYPRE_IJVectorGetObject(x, (void **) &par_x);

    
    hypre_ncols = (uint *) malloc(hypre_nrows * sizeof(uint));
    hypre_rows = (int *) malloc(hypre_nrows * sizeof(int));
    hypre_cols = (int *) malloc(hypre_nrows * sizeof(int));
    hypre_values = (double *) malloc(hypre_nrows * sizeof(double));
  
     // only go to 9, since last one is restart
    for (i = 0; i < hypre_nrows; i++) {
          hypre_ncols[i] = 1;
          hypre_rows[i] = hypre_start + i;
          hypre_cols[i] = hypre_start + i;
          hypre_values[i] = -1;
    }

        // set values in hypre matrix
    HYPRE_IJMatrixAddToValues(A, hypre_nrows, 
                             (int *) hypre_ncols, 
                             (const int *) hypre_rows, 
                             (const int *) hypre_cols, 
                             (const double *) hypre_values);
  
    HYPRE_IJMatrixAssemble(A);
    HYPRE_IJMatrixGetObject(A, (void **) &par_A);
    
    free(hypre_ncols);
    free(hypre_rows);
    free(hypre_cols);
    free(hypre_values);
    
}

HYPRE_ParCSRMatrix * Tmatrix::get_par_A() { return &par_A; }
HYPRE_ParVector * Tmatrix::get_par_b() { return &par_b; }
HYPRE_ParVector * Tmatrix::get_par_x() { return &par_x; }
HYPRE_IJVector * Tmatrix::get_x() { return &x; }
