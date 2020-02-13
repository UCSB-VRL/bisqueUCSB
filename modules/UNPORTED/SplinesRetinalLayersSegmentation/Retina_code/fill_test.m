
clear all;
b = [ 0 1 0 0 0 0
    0 0 0 1 0 0
    1 0 0 0 0 0
    0 1 0 1 0 0
    0 0 1 0 0 0];

b = uint8(b)


max_row_length = size(b,2);
max_column_height = size(b,1);

for j = 1:max_row_length,
    for i = 1:max_column_height,
        if (b(i,j)==uint8(1))
            i=max_column_height+1;
            b
            pause(.003);
            else
            b(i,j)=1;
            b
            pause(.003);
        end
    end
end
         
            