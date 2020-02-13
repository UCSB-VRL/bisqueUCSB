function [im] = getImageFromCell(im,cell)
for j=1:length(cell)
    im(cell(j,2),cell(j,1))=1;
end