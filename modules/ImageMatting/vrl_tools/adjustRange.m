function outVec = adjustRange(inpVec, idr, odr)

%% Function to adjust dynamic ranges of a vector

if( numel(idr)~=2 || numel(odr)~=2 )
    error('Dynamic Ranges are 2 Element Vectors');
end

if( odr(2) <= odr(1) || idr(2) <= idr(1) )
    error('Dynamic Ranges must be sorted in ascending order');
end

intVec = ( inpVec(:) - idr(1) ) / (idr(2)-idr(1));
outVec = ( intVec * (odr(2)-odr(1)) ) + odr(1);

outVec = reshape(outVec, size(inpVec) );
