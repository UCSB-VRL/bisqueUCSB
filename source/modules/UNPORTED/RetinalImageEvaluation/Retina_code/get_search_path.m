function [search_path,I] = get_search_path(im_size,x1,y1,x2,y2)
Y0 = round(y1);X0 = round(x1);
Y1 = round(y2);X1 = round(x2);
search_path = [];
I = [];
if abs(X1 - X0) <= abs(Y1 - Y0)    
    if Y1 < Y0
        k = X1; X1 = X0; X0 = k;
        k = Y1; Y1 = Y0; Y0 = k;
    end
    if (X1 >= X0) && (Y1 >= Y0)
        dy = Y1-Y0; dx = X1-X0;
        p = 2*dx; n = 2*dy - 2*dx; tn = dy;
        while (Y0 <= Y1)
            if tn >= 0
                tn = tn - p;
            else
                tn = tn + n; X0 = X0 + 1;
            end
            search_path = [search_path;Y0,X0];
            Y0 = Y0 + 1;         
        end
    else
        dy = Y1 - Y0; dx = X1 - X0;
        p = -2*dx; n = 2*dy + 2*dx; tn = dy;
        while (Y0 <= Y1)
            if tn >= 0
                tn = tn - p;
            else
                tn = tn + n; X0 = X0 - 1;
            end
            search_path = [search_path;Y0,X0];
            Y0 = Y0 + 1;
            
        end
    end
else
    if X1 < X0
        k = X1; X1 = X0; X0 = k;
        k = Y1; Y1 = Y0; Y0 = k;
    end
    if (X1 >= X0) && (Y1 >= Y0)
        dy = Y1 - Y0; dx = X1 - X0;
        p = 2*dy; n = 2*dx-2*dy; tn = dx;
        while (X0 <= X1)
            if tn >= 0
                tn = tn - p;
            else
                tn = tn + n; Y0 = Y0 + 1;
            end
            search_path = [search_path;Y0,X0];
            X0 = X0 + 1;
        end
    else
        dy = Y1 - Y0; dx = X1 - X0;
        p = -2*dy; n = 2*dy + 2*dx; tn = dx;
        while (X0 <= X1)
            if tn >= 0
                tn = tn - p;
            else
                tn = tn + n; Y0 = Y0 - 1;
            end
            search_path = [search_path;Y0,X0];
            X0 = X0 + 1;            
        end
    end
end


if isempty(search_path)
    return;
end

I = find ( search_path(:,1)<1 | search_path(:,1)>im_size(1) );
search_path(I,:)=[];
I = find ( search_path(:,2)<1 | search_path(:,2)>im_size(2) );
search_path(I,:)=[];

I = sub2ind(im_size,search_path(:,1),search_path(:,2));
