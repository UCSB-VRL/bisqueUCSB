function area = calculateArea(map, layerNum, mag)

% 2005/07/11
% Calulate area within the specified region by map and region num
% in micron
A = find(map==layerNum);
area=length(A)*mag*mag;


