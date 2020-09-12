function [P_A,R_A,P_B,R_B] = Compute_PR(Seg,GT)
%function [P_A,R_A,P_B,R_B] = Compute_PR(Seg,GT)
%
%Computes precision and recall using:
%a) the whole area
%b) only the boundaries
%
%Luca Bertelli, VRL, UCSB
%lbertelli@ece.ucsb.edu

I=double(Seg).*double(GT);
R_A=nnz(I)/nnz(double(GT))*100;
P_A=nnz(I)/nnz(Seg)*100;

edges1=seg2bmap(double(Seg));
edges2=seg2bmap(double(GT));

I=double(edges1).*double(edges2);
R_B=nnz(I)/nnz(double(edges2))*100;
P_B=nnz(I)/nnz(edges1)*100; 

return
