function [arclength]=f_length_trace(Points1)

% set P = to the vertices (x,y) in my_path
P = Points1;

P2 = Points1;

% clear the first row
P2(1,:) = 0;

% shift all rows up one
P2 = circshift(P, -1);

% find (x1-x2, y1-y2)
P1_P2 = P - P2;

% remove last row
P1_P2(length(Points1),:) = [];

% find  [(x1-x2)^2, (y1, y2)^2]
P1_P2 = P1_P2.^2;

sum_of_squares = P1_P2(:,1) + P1_P2(:,2);

arclength = sum(sum(sqrt(sum_of_squares)));

return