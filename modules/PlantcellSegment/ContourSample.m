function Y = ContourSample(EdgeVector, no_sample)

no_EdgePt = size(EdgeVector,1);
step = no_EdgePt / no_sample;
Y = EdgeVector(min(no_EdgePt,round(1 + step * [0:no_sample-1])),:);

