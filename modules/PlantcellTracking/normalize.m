function[im] = normalize(im)

if ~strcmp(class(im),'double')
    im = double(im);
end
im = im - min(min(im));
im = im ./  max(max(im));
end