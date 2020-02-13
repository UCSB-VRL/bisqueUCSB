#include <stdio.h>
#include "mex.h"
#include "graph.hpp"

void mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[])
{
    // Variable Initializations
    int *inp_param;
    double *t_links, *n_links;
    int i;
    if ( (nrhs != 3) || ( mxGetClassID(prhs[0]) != mxINT32_CLASS ) ) 
        mexErrMsgTxt("ERROR1");
    inp_param = (int*)mxGetPr(prhs[0]);
    t_links = (double*)mxGetPr(prhs[1]);    
    n_links = (double*)mxGetPr(prhs[2]);
    typedef Graph<double,double,double> GraphType; // Declaring the graph ...
    GraphType *g = new GraphType( inp_param[1],  (2*inp_param[1]) + (2*inp_param[2]) ); 
    
    g -> add_node(inp_param[1]); // Creating the grid of all nodes put together ... 
    for(i=0; i<inp_param[1] ; i++)  
        g -> add_tweights(i, t_links[2*i], t_links[2*i+1] );
    for(i=0;i<inp_param[2];i++)
        g -> add_edge( n_links[3*i] , n_links[3*i+1] , n_links[3*i+2] , n_links[3*i+2]  );
    int flow = g -> maxflow();
    mexPrintf("Value of flow is %d \n",flow);
    // RETURN VARIABLE
    plhs[0] = mxCreateDoubleMatrix(inp_param[1], 1, mxREAL);
    double* outArray = (double*)mxGetPr(plhs[0]);
    for(i=0;i<inp_param[1];i++)
       outArray[i] = g->what_segment(i); 
    delete g;
    return;
}

