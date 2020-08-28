%%%
%%% HAUSDORFF: Compute the Hausdorff distance between two point clusters
%%%            in an arbitrary dimensional vector space.
%%%            H(A,B) = max(h(A,B),h(B,A)), where
%%%            h(A,B) = max(min(d(a,b))), for all a in A, b in B,
%%%            where d(a,b) is a L2 norm.
%%%   dist = hausdorff( A, B )
%%%     A: the rows of this matrix correspond to points in the first cluster
%%%     B: the rows of this matrix correspond to points in the second cluster
%%%     A and B may have different number of rows, but must have the
%%%     same number of columns (i.e., dimensionality)
%%%   Hany Farid; Image Science Group; Dartmouth College
%%%   10.4.06
%%%   
%%%  Modified line 26 Jose Freire; jmhfreire@gmail.com; CSUSB
%%%    7.21.07 

function [dist] = f_hausdorff_distance( A, B)

if( size(A,2) ~= size(B,2) )
    fprintf( 'WARNING: dimensionality must be the same\n' );
    dist = [];
    return;
end

dist = max( max(compute_dist(A,B)), max(compute_dist(B,A)) );%dist = max( compute_dist(A,B), compute_dist(B,A) );

%%%
%%% Compute distance
%%%
function[ dist ] = compute_dist( A, B )

m = size(A,1);
n = size(B,1);
dim = size(A,2);

dist = zeros(m);

for k = 1 : m
    C = ones(n,1) * A(k,:);
    D = (C-B) .* (C-B);
    D = sqrt( D * ones(dim,1) );
    dist(k) = min(D);
end
dist =max(dist);