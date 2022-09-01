function [D] = diffmethod(I,SW)
% add any diff method that i want to use to this file to try out different
% ones
switch SW
    case 1
        [D1 D2] = gradient(I);
    case 2
        %put wavelet here?
end
D = cat(3,D1,D2);