#ifndef RANDWALK_H
#define RANDWALK_H

#include "common.h"
#include "Args.h"
#include "cells.h"


class RandWalk{

 private:
  uint max_visits;
  uint steps;
  uint * trace;

  float convergence;
  float * steady_state;

  /*
   * how much less likely it is to step to another z-plane than
   * stay in this plane
   */  
  double z_ratio;
  
  imgStack * img;
  cells * img_cells;

  const static pixel offset[BLOCK];

  // inline functions
  void takeStep(pixel & current, pixel & in);

  float dist(float * a, float * b);
  void normalize(float * p, const uint & size);
  void normalize(const uint & size);
  
 public:
  RandWalk(imgStack * img, cells * cells_in, 
	   const double & z_ratio_in);
  ~RandWalk();

  void Walk();

  uint getNumSteps(){ return steps; }
  uint getMaxVisits(){ return max_visits; }
  uint * getTrace(){ return trace; }
  float * getSteadyState(){ return steady_state; }
};

inline void RandWalk::takeStep(pixel & current, 
			       pixel & in){
  uint val;

  current.x = in.x;
  current.y = in.y;
  current.z = in.z;
  ++steps;

  val = ++trace[OFFSET(*img, current)];

  if (val > max_visits){
    max_visits = val;
  }
}

#endif
