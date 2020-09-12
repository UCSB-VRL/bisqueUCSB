function [weights,w_dist] = vrl_edgeweight(edges,vals,lattice_size,sigma,k,scaling)

% [weights,w_dist] = f_edgeweight(edges,vals,lattice_size,sigma,k,scaling)
% Compute the edge weights based on equation below.
%
% w = 1/|p-q|*exp(-|Ip-Iq|^2/2*sigma^2)
%
% INPUTS:
%   edges = M x 2 where each row contains the two nodes defining the edge
%   vals = d x N where N is the total # of nodes, d is the dimension of the
%          data/feature at each node
%   lattice_size = [r c z] array specifying the dimensions of the node lattice
%   sigma = scalar parameter specifying intensity at half-max
%   k = scalar parameter controling the norm order (default is 2)
%   scaling = [dr dc dz] array specifying the relative scaling of distances
%           in each dimension.
% OUTPUT:
%   weights = M x 1 weights corresponding to each edge
%   w_dist = M x 1 euclidian distance of node pairs connected by edges.
%
% Nhat Vu
% 06.25.2007

if max(edges(:)) > length(vals),
    error('edge index exceeds number of elements in vals');
end

if max(edges(:)) > prod(lattice_size),
    error('edge index exceeds number of elements in lattice');
end

if ~exist('k','var'),
    k = 2;
end

% create lattice of points
if length(lattice_size) < 3,
    z = 1;
else
    z = lattice_size(3);
end

r = lattice_size(1);
c = lattice_size(2);

[X,Y,Z] = meshgrid(1:c,1:r,1:z);

% scaling
if nargin < 6,
    scaling = [1 1 1];
end
X = scaling(1)*X;
Y = scaling(2)*Y;
Z = scaling(3)*Z;

% compute euclidian distances between adjoining nodes
w_dist = sqrt( (X(edges(:,1))-X(edges(:,2))).^2 + (Y(edges(:,1))-Y(edges(:,2))).^2 + (Z(edges(:,1))-Z(edges(:,2))).^2 );
if r==1,
    w_dist = w_dist';
end
% compute feature distances between adjoining nodes
d = size(vals,1);
if d == 1,
    w_feat = abs(vals(edges(:,1))-vals(edges(:,2))).^k;
else
    w_feat = sum(abs(vals(:,edges(:,1))-vals(:,edges(:,2))).^k);
end

if ~exist('sigma','var'),
    sigma = sqrt(mean(w_feat));
elseif isempty(sigma),
    sigma = sqrt(mean(w_feat));
end

weights = 1./w_dist.*exp(-1/(2*sigma.^2)*w_feat)';

% tempImg1 = zeros(lattice_size(1), lattice_size(1));
% tempImg2 = zeros(lattice_size(1), lattice_size(1));
% tempImg1( edges(:,1) ) = weights; tempImg2( edges(:,2) ) = weights;
% figure(1); imagesc( (tempImg1 + tempImg2 ) / 2); title([num2str(sigma) ] );
return;
% if d == 1,
%     weights = 1./w_dist.*(exp(-1/(2*sigma.^2)*(abs(vals(edges(:,1))-vals(edges(:,2)))).^k))';
% else
%     weights = 1./w_dist.*(exp(-1/(2*sigma.^2)*sum((abs(vals(:,edges(:,1))-vals(:,edges(:,2))).^k))))';
% end