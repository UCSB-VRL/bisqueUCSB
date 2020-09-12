function [I] = handleFLIP(I)
% handle the direction
[direc] = DC(I);   
switch direc
   case 1                                                      % from the left
       % do nothing
   case 2                                                      % from the right
       I = fliplr(I);                   
   case 3                                                      % from the top
       return            
   case 4                                                      % from the bottom
       return
end
% handle the direction   
% read and flip