function generate_text_fileOUTPUT(A,frameNum)

A = A';
outFname = ['out' num2str(frameNum) '.txt'];
fid = fopen(outFname,'w');
fprintf(fid,'%6.2f %12.4f\n',A);
fclose(fid);
