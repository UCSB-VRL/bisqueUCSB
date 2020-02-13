#include <iostream>
#include <fstream>
#include <cmath>

#include "RandWalk.h"

using namespace std;

/*
 * Update determines how often we compute the norm of the vector.
 * For very large images, this computation is extremely time consuming so
 * lower values here will result in *much* higher run times.
 */
const uint UPDATE    = 100;
const uint MAX_ITERS = 3000;
/*
 * This designates a number of restarts to complete before we start
 * to compute the vector norms. The number of restarts needed before
 * we drop below the tolerance level varies a lot, so this should remain 
 * fairly low (not greater than 350)
 */
const uint MIN_ITERS = 200;
/*
 * OPT_TOLERANCE is an input parameter
 * The default (as of 9/7/07) is set to 0.25 and seems to work very well
 * for the horizontal cell images
 */


const  
pixel RandWalk::offset[BLOCK] = {{-1, 1, -1}, {-1, 0, -1}, {-1, -1, -1}, 
				 {0, 1, -1}, {0, 0, -1},  {0, -1, -1},
				 {1, 1, -1}, {1, 0, -1},  {1, -1, -1},
				 {-1, 1, 0}, {-1, 0, 0},  {-1, -1, 0}, 
				 {0, 1, 0},  {0, 0, 0},   {0, -1, 0},
				 {1, 1, 0},  {1, 0, 0},   {1, -1, 0},
				 {-1, 1, 1}, {-1, 0, 1},  {-1, -1, 1}, 
				 {0, 1, 1},  {0, 0, 1},   {0, -1, 1},
				 {1, 1, 1},  {1, 0, 1},   {1, -1, 1}};

RandWalk::RandWalk(imgStack * img_in, cells * cells_in, 
		   const double & z_ratio_in){
  img       = img_in;
  img_cells = cells_in;

  steady_state = (float *)malloc(img->height * 
				  img->width * 
				  img->depth * sizeof(float));
  
  trace        = (uint *) calloc(img->height * 
				 img->width * 
				 img->depth, sizeof(uint));

  if ((steady_state == NULL) || (trace == NULL)){
    cerr << "Could not allocate arrays in RandWalk constructor.\n";
  }
  
  convergence = 99999;
  max_visits  = 0;
  steps       = 0;

  z_ratio = z_ratio_in;
}

RandWalk::~RandWalk(){
  free(trace);
  free(steady_state);

  /*
   * don't call free for cells or imgStack pointers
   * because those are owned by other objects
   */
}

void RandWalk::Walk(){
  uint i, last_pos, w = 0;
  float sum, intensities[BLOCK];
  float tally, guess;
  pixel current, next[BLOCK], center = img_cells->getThisCell();
  uint size = img->height * img->width * img->depth;

  double c;
  float * last = (float *) calloc(size, sizeof(float));

  bool restart = false;
  time_t timer_start, timer_stop, walk_start, walk_stop;

  if (OPT_DEBUG > 0){
    cout << "Z Ratio: " << z_ratio << endl << endl;
    cout << "** Starting Random Walk Simulation **\n";
  }

  if (center.z >= (int)img->depth){
    cout << "Warning: Reseting Z component of cell center to the first plane.\n";
    center.z = 0;
  }


  timer_start = time(NULL);
  walk_start  = time(NULL);

  // Number of walks to compute
  while (w <= MAX_ITERS){
  
    if ((OPT_DEBUG > 0) && (w % UPDATE == 2)){
      walk_stop = time(NULL);
      
      cout << endl 
	   << "Distance   : " << convergence << endl
	   << "Max visits : " << max_visits << endl
	   << "restarts   : " << w << endl
	   << "Time       : " << difftime(walk_stop, walk_start) << endl;
      
      walk_start = time(NULL);
    }
    ++w;
    
    takeStep(current, center);

    while (! restart){
      c = img_cells->adjustRestart(current, img) * RAND_MAX;
      if (rand() < c){
	restart = true;
	break;
      }

      sum = 0;
      for (i = 0; i < BLOCK; i++) {
	// get neighbors
	next[i].x = current.x + offset[i].x;
	next[i].y = current.y + offset[i].y;
	next[i].z = current.z + offset[i].z;
	
	if (((next[i].z >= 0) && (next[i].z < (int)img->depth)) &&
	    ((next[i].y >= 0) && (next[i].y < (int)img->height)) &&
	    ((next[i].x >= 0) && (next[i].x < (int)img->width))){
	  
	  // account for different z-planes being further away
	  if (next[i].z != current.z){
	    // pixels in different planes need to be weighted less
	    intensities[i] = z_ratio * img->image_stack[OFFSET(*img, next[i])];
	  }else{
	    intensities[i] = (float)img->image_stack[OFFSET(*img, next[i])];
	  }
	  sum += intensities[i];
	}else{
	  intensities[i] = -1;
	}
      }


      // make decision of where to step
      guess = (sum * 1.0 * rand() / (RAND_MAX + 1.0));
      tally = 0;
      for (i = 0; i < BLOCK; ++i) {
	if (intensities[i] == -1){
	  continue;
	}

	tally += intensities[i];

	if (tally >= guess){
	  break;
	}
      }
      last_pos = i;
      takeStep(current, next[i]);
    }
    restart = false;

    if (w >= MIN_ITERS){
      /*
       * Every UPDATE restarts, we compute the L2 norm between 2 consecutive runs
       * to check for convergence
       */

      if ((w % UPDATE) == 0){
	normalize(last, size);

      }else if ((w % UPDATE) == 1){
	normalize(size);
	convergence = dist(steady_state, last);
	
	if (convergence < OPT_TOLERANCE){
	  break;
	}
      }
    }
  }

  timer_stop = time(NULL);
  
  if (fout.is_open()){
    fout << "Random Walk finished in: " << difftime(timer_stop, timer_start)
	 << " seconds" << endl 
	 << "Distance               : " << convergence << endl
	 << "Total steps            : " << steps << endl
	 << "Total restarts         : " << w << endl
	 << "Maximum visits         : " << max_visits << endl << endl;
  }

  cout << endl;
  cout << "Random Walk finished in: " << difftime(timer_stop, timer_start)
       << " seconds" << endl 
       << "Distance               : " << convergence << endl
       << "Total steps            : " << steps << endl
       << "Total restarts         : " << w << endl
       << "Maximum visits         : " << max_visits << endl;
  cout << endl;
  
  normalize(size);
}

void RandWalk::normalize(const uint & size){
  uint i;
  
  for (i = 0; i < size; ++i){
    steady_state[i] = (float)(trace[i]) / (float)max_visits;
  }
}


void RandWalk::normalize(float * p, const uint & size){
  uint i;

  for (i = 0; i < size; ++i){
    p[i] = (float)(trace[i]) / (float)max_visits;
  }
}


float RandWalk::dist(float * a, float * b){
  uint i;
  uint size = img->height * img->width * img->depth;
  float tmp, distance = 0.0;

  for (i = 0; i < size; ++i){
    tmp = a[i] - b[i];
    distance += (tmp * tmp);
  }
  
  distance = sqrt((double)distance);
  
  return distance;
}
