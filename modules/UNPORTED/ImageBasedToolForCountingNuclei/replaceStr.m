function outStr=replaceStr(a,b,c)

% find a substing b from a and replace with c
% for example replaceStr('img_normalize.tif', '_normalize','_equalize')
% returns  img_equalize.tif

ind =findstr(a,b);
offset = length(c)-length(b);
if isempty(ind)
    outStr = a;
else
    if offset ==0
        for k=1: length(ind)
            a = [ a(1: ind(k)+offset*(k-1)-1),c, a(ind(k)+ 1: length(a))];
        end
    else

        for k=1: length(ind)
            a = [ a(1: ind(k)+offset*(k-1)-1),c, a(ind(k)+ length(b)*k: length(a))];
        end
    end
            outStr = a;
end