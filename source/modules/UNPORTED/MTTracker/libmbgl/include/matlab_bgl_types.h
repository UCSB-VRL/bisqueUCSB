#ifndef MATLAB_BGL_TYPES_H
#define MATLAB_BGL_TYPES_H

/*
 * David Gleich
 * 19 February 2007
 * Copyright, Stanford University, 2007
 */

/**
 * @file matlab_bgl_types.h
 * Implement a series of types for the matlab_bgl project to support
 * large sparse matrices on 64-bit platforms.
 */

#ifdef MATLAB_BGL_LARGE_ARRAYS
#include <stdlib.h>
typedef size_t mbglIndex;
#else
typedef int mbglIndex;
#endif /* MATLAB_BGL_LARGE_ARRAYS */

#endif /* MATLAB_BGL_TYPES_H */
