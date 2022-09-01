function v = scalev(v)
    if max(v)<=min(v),
        v = ones(length(v),1);
    else
        v = ( v - min(v) ) / ( max(v) - min(v) );
    end
end