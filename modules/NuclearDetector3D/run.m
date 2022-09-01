nuclear_channel = 0;
nuclear_diameter = 2.6;

files =dir('..\');
for i=1:length(files),
    filename = ['..\' files(i).name];
    if length(filename)>2 && strcmp(filename(end-2:end), 'tif')==1,
        run_local(filename, nuclear_channel, nuclear_diameter);
    end
end
