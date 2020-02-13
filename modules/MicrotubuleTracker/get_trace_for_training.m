function coarse_traces = get_trace_for_training(im)

coarse_traces = [];
button = 'l';

while button ~= 'q' && button ~= 'Q'
    figure, imshow(imadjust(im)); title('Select points on center of the microtubule body');
    [x, y] = (getline());
    x = round(x); y = round(y);
    coarse_traces = [coarse_traces;[x y]];
end