function generate_text_file(im)

delete('tempp.txt');
if numel(size(im))==4
    im=rgb2gray(im);
end

im=mat2gray(im);
imshow(im);
hold on
[Ix Iy] = ginput(6);
A = [Ix,Iy];A=A';
fid = fopen('tempp.txt','w');
fprintf(fid,'%6.2f %12.4f\n',A);
fclose(fid);
A=A';