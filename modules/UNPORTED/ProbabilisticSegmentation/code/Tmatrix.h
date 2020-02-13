#ifndef T_MATRIX_H
#define T_MATRIX_H

#include <iostream>
#include <mpi.h>
#include "common.h"
#include "cells.h"
#include "_hypre_utilities.h"
#include "HYPRE_krylov.h"
#include "HYPRE.h"
#include "HYPRE_parcsr_ls.h"

using namespace std;


class Tmatrix{

 private:
  HYPRE_IJMatrix A;
  HYPRE_ParCSRMatrix par_A;
  HYPRE_IJVector b;
  HYPRE_ParVector par_b;
  HYPRE_IJVector x;
  HYPRE_ParVector par_x;

  imgStruct img;
  cells * img_cells;
  hypreCol t;

  /*
   * Allows each processor to contain up to 4e9 elements
   * - can be expanded to "unsigned long long" to allow
   * up to 1.84e19 elements
   */
  uint start, stop;
  uint hypre_start, hypre_stop;
  uint rank, nproc;
  ulong nnz;
  
  static const double move_mask[BLOCK][BLOCK];
  static const uint come_from[BLOCK];
  
  /*
   * Calculates the sum of the intensities of a 3x3 block centered around
   * the pixel at index
   */
  uint blockIntensity(pixel in, pixel neighbors[], double probs[]);
  
  
  /*
   * Finds the neighboring pixels (x,y positions) of 'in'
   */
  void getNeighbors(pixel in, pixel neighbors[]);
  
  /*
   * Calculates the probabilities of visiting each of the pixels in the 3x3
   * block by dividing the intensity value at that pixel in the image by 
   * the total intensity summed over the entire block
   */
  void getProbabilities(uint total, pixel neighbors[], double probs[]);
  
  /*
   * Multiply momentum values (denoted by the direction input) by the
   * probs[] array
   */
  void calcPixel(pixel index, pixel neighbors[], double probs[]);

  void reNormalize();

  void setPixel(hypreCol tpixel);
 

  void setRestart();
  void initVectors();
  void finalize();

 public:
  
  Tmatrix(ushort * image, 
	  uint height, uint width, 
	  uint start_in, uint stop_in, 
	  uint rank_in, uint nproc_in);
  
  /*
   * Adds all cell centers from the image, distinguishing the cell you 
   * would like to segment from the rest of the image
   */
  void addCells(pixel * centers_in, uint cell_count, double restart, int segcell);
  pixel getCurrentCell(){ return img_cells->getThisCell(); }

  int Build();
  
  HYPRE_ParCSRMatrix * get_par_A();
  HYPRE_ParVector * get_par_b();
  HYPRE_ParVector * get_par_x();
  HYPRE_IJVector * get_x();
  //hypreCol * BuildPixel();
};


#endif
