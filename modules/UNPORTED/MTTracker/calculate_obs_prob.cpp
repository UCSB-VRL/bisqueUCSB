

#include "mex.h"
#include <math.h>
#include <vector>


int max_index(std::vector<double> &temp){
	double max_val = temp[0];
	int max_ind = 0;
	int size = temp.size();
	
	for(int m = 1 ; m < size; m++)
	{
		if (temp[m]>max_val)
		{
			max_val = temp[m];
			max_ind = m;
		}
	}
	return max_ind;
}

int min_index(std::vector<double> &temp){
	double min_val = temp[0];
	int min_ind = 0;
	int size = temp.size();
	
	for(int m = 1 ; m < size; m++)
	{
		if (temp[m]<min_val)
		{
			min_val = temp[m];
			min_ind = m;
		}
	}
	return min_ind;
}

double GetReal2D(mxArray* mat, int row, int col){
	
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

void SetReal3D(mxArray* mat, int idx0, int idx1, int idx2, double val){
	
	double *mat_data = mxGetPr(mat);
	int num_d0 = mxGetDimensions(mat)[0];
	int num_d1 = mxGetDimensions(mat)[1];
	int num_d2 = mxGetDimensions(mat)[2];
	
	if (idx0 >= 0 && idx0 < num_d0 
		&& idx1 >= 0 && idx1 < num_d1
		&& idx2 >= 0 && idx2 < num_d2)
		mat_data[idx0+idx1*num_d0+idx2*num_d0*num_d1] = val;
}

double GetReal3D(mxArray* mat, int idx0, int idx1, int idx2){
	
	double *mat_data = mxGetPr(mat);
	int num_d0 = mxGetDimensions(mat)[0];
	int num_d1 = mxGetDimensions(mat)[1];
	int num_d2 = mxGetDimensions(mat)[2];
	
	if (idx0 >= 0 && idx0 < num_d0 
		&& idx1 >= 0 && idx1 < num_d1
		&& idx2 >= 0 && idx2 < num_d2)
		return mat_data[idx0+idx1*num_d0+idx2*num_d0*num_d1];
	else
		return 0.0;
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

double exp_pdf(double val, double mean, double std){
	
	return 1/sqrt(2.0*3.14159265)/std*exp(-0.5*pow(val-mean,2.0)/pow(std,2.0));
	
	
}

void mexFunction( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] )
{
	int dims[3];
	
	std::vector<double> dead_state_prob;
	
	mxArray *tmp;
	

	
	mxArray *vx = mxGetField(prhs[0],0,"vx");
	mxArray *vy = mxGetField(prhs[0],0,"vy");

	
	
	
	mxArray *gxx = mxGetField(prhs[1],0,"gxx");
	mxArray *gxy = mxGetField(prhs[1],0,"gxy");
	mxArray *gyy = mxGetField(prhs[1],0,"gyy");
	
	double fg_mean = mxGetScalar(mxGetField(prhs[2],0,"m"));
	double fg_std = mxGetScalar(mxGetField(prhs[2],0,"s"));
	
	double bg_mean = mxGetScalar(mxGetField(prhs[3],0,"m"));
	double bg_std = mxGetScalar(mxGetField(prhs[3],0,"s"));	
	
	int N = mxGetDimensions(vx)[0];
	int T = mxGetDimensions(vx)[1];
	
	dims[0] = N+2;
	dims[1] = N+2;
	dims[2] = T-1;
	
	dead_state_prob.resize(N*N);
	
	
	plhs[0] = mxCreateNumericArray(3, dims, mxDOUBLE_CLASS, mxREAL);
	mxArray *output = plhs[0];
	
	
	for (int t = 0 ; t < T-1 ; t++)
	{
		for(int n1 = 0, k = 0 ; n1 < N ; n1++)
		{
			for(int n2 = 0 ; n2 < N ; n2++,k++)
			{
				double deriv = calculate_d_deriv(gxx, gxy, gyy, 
												 GetReal2D(vx,n1,t)-1.0, GetReal2D(vy,n1,t)-1.0, 
												 GetReal2D(vx,n2,t+1)-1.0, GetReal2D(vy,n2,t+1)-1.0, 10);
				dead_state_prob[k] = exp_pdf(deriv, bg_mean, bg_std);
				SetReal3D(output,n1,n2,t,exp_pdf(deriv, fg_mean, fg_std));
			}
		}
		
		int min_ind = min_index(dead_state_prob);
		
		for(int n1 = 0; n1 < N ; n1++)
		{
			std::vector<double> temp(N);
			for(int n2 = 0 ; n2 < N ; n2++)
				temp[n2] = GetReal3D(output, n1, n2, t);
			
			int max_ind = max_index(temp);
			SetReal3D(output,N,n1,t,std::min(dead_state_prob[min_ind],temp[max_ind]));
			SetReal3D(output,n1,N+1,t,std::min(dead_state_prob[min_ind],temp[max_ind]));
			//SetReal3D(output,n1,N+1,t,dead_state_prob[min_ind]);
			//SetReal3D(output,n1,N+1,t,(dead_state_prob[min_ind]+temp[max_ind])/2.0);
		}
			
		SetReal3D(output,N,N,t,dead_state_prob[min_ind]);
		SetReal3D(output,N,N+1,t,0.0);
		
		for(int n1 = 0 ; n1 < N ; n1++)
			SetReal3D(output,N+1,n1,t,0.0);
		SetReal3D(output,N+1,N,t,0.0);
		SetReal3D(output,N+1,N+1,t,dead_state_prob[min_ind]);
		
		for(int n1 = 0 ; n1 < N ; n1++)
			SetReal3D(output,n1,N,t,0.0);
		

	}

	
	
	//SetReal3D(output,2,3,8,10.0);
	

//	for (int i = 0 ; i < 5*5*15 ; i++)
//		output[i] = (double) i;
}