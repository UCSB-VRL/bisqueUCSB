#ifndef CELLS_H
#define CELLS_H

#include <cmath>
#include <string>

#include "common.h"

using namespace std;

/*
 * Expand cells class to handle points which are known to not
 * be in the cell of interest in addition to other cells
 *
 * Allow users to segment an entire image without rebuilding
 * most of the transition matrix??
 */

class cells{

 private:
  uint cur_cell_index;
  uint cell_cnt;

  pixel * cell_centers;
  double z_ratio, restart;
  double * distances;
  
  double normAdjust(const imgStack * img, double & my_dist);

  double dist(const pixel & index, const pixel & cell);

  // helper function for readCells()
  static bool getIndices(string & line, string::size_type & idx1, string::size_type & idx2);
  
 public:

  cells(pixel * centers, 
	const uint & cnt, 
	const double & c, 
	const uint & segcell,
	const double & z_ratio_in);
  ~cells();

  // ------------------ Get methods ------------------
  pixel getThisCell(){ return cell_centers[cur_cell_index];}
  double getRestart(){ return restart; }
  uint getCellCount(){ return cell_cnt; }
  bool insideMyCell(pixel & index);

  int updateCenters(pixel & max_dims);

  /*
   * Returns the distance between 2 cells, given their indices
   */
  //double cellDists(uint i, uint j){ return cell_dists[i][j]; }

  /*
   * Returns a distance between the current pixel and
   * the current cell center (the cell we are segmenting)
   */
  double distFromCurrentCell(const pixel & index);

  /*
   * Returns an array of distances
   * A distance between the current pixel index and each 
   * of the 'other' cells (not the one we are segmenting)
   */
  double * distFromCells(const pixel & index);

  /*
   * Finds the cell (from the 'other cells') the current pixel is closest to
   */
  double minDistFromCells(const pixel & index);

  /*
   * Adjusts the restart probability based on the given
   * pixel's distance from each of the cells
   */ 
  double adjustRestart(const pixel & index,
		       const imgStack * img);

  /*
   * Parses the input file and grabs the relevant information
   * about the cells
   */
  static pixel * readCells(const char * file, 
			   uint & cell_cnt);
			   
};

inline double cells::dist(const pixel & index, const pixel & cell){
  double x = (index.x - cell.x);
  double y = (index.y - cell.y);
  double z = (index.z - cell.z);
  double mult = (1 / z_ratio);

  return (sqrt((x * x) + (y * y) + ((mult * z) * (mult * z))));
}

#endif
