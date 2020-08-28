function segmentation = htseg(i, threshold)
    %htseg(i, threshold) - histogram threshold segmentation
    %usage:
    %   i           image matrix
    %   threshold   threshold of color range
    
    g = rgb2gray(i);
    segmentation = roicolor(g, 0, threshold);
    
    
    
end