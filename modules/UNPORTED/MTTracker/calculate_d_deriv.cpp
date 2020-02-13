

#include "mex.h"
#include <math.h>
#include <vector>



double GetReal2D(const mxArray* mat, int row, int col){
	
	double *mat_data = mxGetPr(mat);
	int num_rows = mxGetM(mat);
	int num_cols = mxGetN(mat);
	
	if (row >= 0 && row < num_rows && col >= 0 && col < num_cols)
		return mat_data[row+col*num_rows];
	else
		return 0.0;
}

void SetReal2D(mxArray* mat, int row, int col, double val){
	
	double *mat_data = mxGetPr(mat);
	int num_rows = mxGetM(mat);
	int num_cols = mxGetN(mat);
	
	if (row >= 0 && row < num_rows && col >= 0 && col < num_cols)
		mat_data[row+col*num_rows] = val;
}

double interp2d(mxArray* img, double pt_x, double pt_y){
	
	double b1,b2,b3,b4;
	int fx,fy,cx,cy;
	
	
	fx = floor(pt_x); fy = floor(pt_y);
	cx = ceil(pt_x); cy = ceil(pt_y);
	
	b1 = GetReal2D( img, fy, fx );
	b2 = GetReal2D( img, fy, cx ) - b1;
	b3 = GetReal2D( img, cy, fx ) - b1;
	b4 = b1 - GetReal2D( img, cy, fx ) - GetReal2D( img, fy, cx ) + GetReal2D( img, cy, cx );
	

	double fi = b1 + b2*(pt_x-(double)fx) + b3*(pt_y-(double)fy) + b4*(pt_x-(double)fx)*(pt_y-(double)fy);
	
	
	return fi;
}

void linspace(std::vector<double> &f, double d1 ,double d2, int num_pts){
	f.resize(num_pts);
	for(int i = 0 ; i < num_pts ; i++)
	{
		f[i] = d1 + (double)i*(d2-d1)/((double)num_pts-1.0);	
	}
}

double calculate_d_deriv(mxArray* gxx, mxArray* gxy, mxArray* gyy, double start_x, double start_y, double end_x, double end_y, int num_pts){
	
	std::vector<double> gxxi(num_pts);
	std::vector<double> gxyi(num_pts);
	std::vector<double> gyyi(num_pts);
	std::vector<double> f(num_pts);
	std::vector<double> pts_i_x;
	std::vector<double> pts_i_y;
	
	double d_x = start_x - end_x;
	double d_y = start_y - end_y;
	double norm = sqrt(d_x * d_x + d_y * d_y);
	double cos_alpha = -d_y/norm;
	double sin_alpha = d_x/norm;
	
	linspace(pts_i_x, start_x, end_x, num_pts);
	linspace(pts_i_y, start_y, end_y, num_pts);
	

	for (int i = 0 ; i < num_pts ; i++){
		gxxi[i] = interp2d(gxx, pts_i_x[i], pts_i_y[i]);
		gxyi[i] = interp2d(gxy, pts_i_x[i], pts_i_y[i]);
		gyyi[i] = interp2d(gyy, pts_i_x[i], pts_i_y[i]);
	}
	
	for( int i = 0; i < num_pts ; i++)
	{
		f[i] = gxxi[i]*cos_alpha*cos_alpha + 2.0*gxyi[i]*cos_alpha*sin_alpha + gyyi[i]*sin_alpha*sin_alpha;	
	}
	
	
	double sum = 0.0;
	
	for (int i = 0 ; i < num_pts; i++)
	{
		sum += f[i];
	}
	sum /= (double)num_pts;

	
	return -sum;
	
	
}

void mexFunction( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] )
{

	mxArray *gxx = mxGetField(prhs[0],0,"gxx");
	mxArray *gxy = mxGetField(prhs[0],0,"gxy");
	mxArray *gyy = mxGetField(prhs[0],0,"gyy");
	
	
	const mxArray *start_x = prhs[1];
	const mxArray *end_x = prhs[2];
	const mxArray *start_y = prhs[3];
	const mxArray *end_y = prhs[4];
	
	
	int num_pts = mxGetM(start_x);
	
	plhs[0] = mxCreateNumericMatrix(num_pts, 1, mxDOUBLE_CLASS, mxREAL);
	
	for (int i = 0 ; i < num_pts ; i++)
	{
						
		double deriv = calculate_d_deriv(gxx, gxy, gyy, 
										GetReal2D(start_x,i,0)-1.0, GetReal2D(start_y,i,0)-1.0, 
										GetReal2D(end_x,i,0)-1.0, GetReal2D(end_y,i,0)-1.0, 10);
		SetReal2D(plhs[0], i, 0, deriv);
		
	}

}