#include <cmath>
#include <iostream>
#include <fstream>

#include "cells.h"
#include "Args.h"

using namespace std;

// Min and Max Macros
#define MIN(X,Y) ((X) < (Y) ? (X) : (Y))
#define MAX(X,Y) ((X) > (Y) ? (X) : (Y))


cells::cells(pixel * centers, 
	     const uint & cnt, 
	     const double & c, 
	     const uint & segcell,
	     const double & z_ratio_in){
  cur_cell_index = 0;

  if ((cnt <= 0) || (centers == NULL)){
    cerr << "No cells were entered!\n";
    return;
  }

  z_ratio  = z_ratio_in;
  cell_cnt = cnt;
  restart  = c;

  cell_centers = centers;
  /*
  cell_centers = (pixel *) malloc(cell_cnt * sizeof(pixel));
  for (i = 0; i < cell_cnt; ++i){
    cell_centers[i] = centers[i];
  }
  */

  if (segcell < cell_cnt){
    cur_cell_index = segcell;
  }else{
    cerr << "WARNING: Invalid cell picked for segmentation. Segmenting cell 0\n";
  }

  // check that there are other cells in the image
  if (cell_cnt <= 1){
    distances    = (double *) malloc(1 * sizeof(double));
    distances[0] = 0;
  }else{
    distances = (double *) malloc((cell_cnt - 1) * sizeof(double));
  }
}

cells::~cells(){
  //free(cell_centers);
  free(distances);
}

double * cells::distFromCells(const pixel & index){
  uint j = 0, i = 0;
  pixel cell;

  // check that there are other cells in the image
  if (cell_cnt <= 1){
    return distances;
  }

  while (i < cell_cnt){
    if (i == cur_cell_index){
      ++i;
      continue;
    }
    
    cell         = cell_centers[i];
    distances[j] = dist(index, cell);

    ++j;
    ++i;
  }
  
  return distances;
}


double cells::minDistFromCells(const pixel & index){
  uint i;
  double min_dist    = 999.9;
  double * distances = distFromCells(index);

  if (cell_cnt <= 1){
    min_dist = 0;

    return min_dist;
  }

  for (i = 0; i < (cell_cnt - 1); ++i){
    if (min_dist > distances[i]){
      min_dist = distances[i];
    }
  }

  return min_dist;
}

double cells::distFromCurrentCell(const pixel & index){
  return dist(index, cell_centers[cur_cell_index]);
}

double cells::adjustRestart(const pixel & index, 
			    const imgStack * img){
  double c_adjusted;
  double my_dist        = distFromCurrentCell(index);
  double min_other_dist = minDistFromCells(index);

  if (my_dist <= AREA){
    /*
     * We are definately inside our own cell
     */
    c_adjusted = 0.0;
    
  }else{  
    
    if (cell_cnt <= 1){
      if (OPT_NORMADJ_RESTART){
	c_adjusted = normAdjust(img, my_dist);
      }else{
	c_adjusted = restart;
      }
    }else if (min_other_dist < my_dist){
      /*
       * We are closer to another cell than
       * we are to our own cell
       */
      
      if (min_other_dist <= AREA){
	/*
	 * We are inside another cell, so 
	 * set restart probability to 1
	 */
	
	c_adjusted = 1.0;
      }else{
	/*
	 * We are closer to another cell than to our
	 * own, so we increase restart probability by a function
	 * of the two distances
	 */
	
	c_adjusted  = MIN(MAX_DIST, (my_dist / min_other_dist));
	c_adjusted /= MAX_DIST;
      }
    }else{
      /*
       * We're not closer to another cell, but we could still
       * be moving farther away from our own cell
       *
       * slighlty increase restart as we move to infinity
       * as dist -> inf, c -> 2*c
       */

      if (OPT_NORMADJ_RESTART){
	c_adjusted = normAdjust(img, my_dist);
      }else{
	c_adjusted = restart;
      }
    }
  }    
  
  return c_adjusted;
}

double cells::normAdjust(const imgStack * img, 
			 double & my_dist){
  double c_adjusted;

  pixel s = cell_centers[cur_cell_index];
  double max_x = MAX(((uint)s.x), (img->width  - s.x));
  double max_y = MAX(((uint)s.y), (img->height - s.y));
  double max_z = MAX(((uint)s.z), (img->depth  - s.z));
  double max_dist = MAX(max_x, max_y);
  max_dist = MAX(max_dist, max_z);
  
  double adjustment = pow((double)(my_dist / max_dist), EXP);
  
  c_adjusted = restart + (restart * adjustment);

  return c_adjusted;
}

bool cells::insideMyCell(pixel & index){
  double my_dist = distFromCurrentCell(index);

  return (my_dist <= AREA);
}



/*
 * Static functions for Parsing input file
 */
bool cells::getIndices(string & line, string::size_type & idx1, string::size_type & idx2){
  const uint DELIMS = 4;
  const string delims[] = {",", " ", "\t", ":"};
  uint x = 0;
  
  // find the delim character (defined above) in the line
  idx1 = string::npos;
  idx2 = string::npos;
  
  while ((idx1 == string::npos) && (x < DELIMS)){
    idx1 = line.find(delims[x], 0);
    ++x;
  }

  // make sure we found something or else quit
  if (idx1 == string::npos){
    return false;
  }

  x = 0;
  while ((idx2 == string::npos) && (x < DELIMS)){
    idx2 = line.find(delims[x], (idx1 + 1));
    ++x;
  }
  
  // make sure we found something or else quit
  if (idx2 == string::npos){
    return false;
  }

  return true;
}


/*
 * Reads in a file in the following format:
 * first line: number of cells in image
 * consecutive lines: x,y,z
 * where x,y,z are the cell centers
 */
pixel * cells::readCells(const char * file, 
			 uint & cell_cnt){
  pixel * cells = NULL;
  ifstream in;

  cell_cnt = 0;
  
  in.open(file);
  if (! in.is_open()){
    cerr << "Could not open cell definition file. (" << file << ")\n";
    return NULL;
  }else{
    string line;
    string::size_type idx1, idx2;
    uint i = 0;

    // find out how many cells are in the image
    getline(in, line);
    
    // set count and allocate space for array
    cell_cnt = atoi(line.c_str());
    if (cell_cnt <= 0){
      return NULL;
    }
    cells = (pixel *) malloc(cell_cnt * sizeof(pixel));

    if (OPT_SEGCELL >= cell_cnt){
      cerr << "Invalid Starting Cell. Segmenting Cell 0\n";
      OPT_SEGCELL = 0;
    }

    while ((i < cell_cnt) && (! in.eof())){
      getline(in, line);
      
      getIndices(line, idx1, idx2);

      // take the string before the comma to be the x coord.
      // the string after the comma as the y coord.
      cells[i].x = atoi(line.substr(0, idx1).c_str());
      cells[i].y = atoi(line.substr((idx1 + 1), (idx2 - idx1)).c_str());
      cells[i].z = atoi(line.substr(idx2 + 1).c_str());
      
      ++i;
    }

    if (OPT_DEBUG){
      cout << endl;
      cout << cell_cnt << " cells found.\n";

      for (i = 0; i < cell_cnt; ++i){
	cout << cells[i].x << ", " 
	     << cells[i].y << ", " 
	     << cells[i].z << endl;
      }
      cout << endl;
    }
  }

  return cells;
}

int cells::updateCenters(pixel & max_dims){
  uint i = 0;
  int ret = 1;
  pixel tmp;

  while ((i < cell_cnt) && (ret == 1)){
    tmp = cell_centers[i];

    if (((tmp.x < 0) || (tmp.x > max_dims.x)) ||
	((tmp.y < 0) || (tmp.y > max_dims.y))){
      cerr << "Error: Invalid x,y coordinate for cell center " << i << endl;
      ret = 0;
    }

    if ((tmp.z < 0) || (tmp.z > max_dims.z)){
      cell_centers[i].z = 0;
      cout << "Warning: reseting cell center " << i << " to the first plane\n";
    }
      
    ++i;
  }
  
  return ret;
}
