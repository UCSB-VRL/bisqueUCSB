%% Find a 'classpath.txt' file

clpath = which('classpath.txt');

%% Make a copy of original 'classpath.txt' - > 'classpath_old.txt'

% p = regexpi(clpath, 'classpath.txt');
% pn = clpath(1:p-1);
% fn = clpath(p:length(clpath));
% [pathstr, name, ext, versn] = fileparts(fn);
% clpath_old = [pn name '_old' ext];
%copyfile(clpath, clpath_old)

%% Open classpath.txt file
% classpaths_cell= {};
% fid = fopen(clpath);
% if fid==-1
%   error('File not found or permission denied');
% end
% i = 1;
% while 1
%     tline = fgetl(fid);
%     if ~ischar(tline),   break,   end
%     disp(tline)
%     classpaths_cell{i,1} = tline;
%     i = i + 1;
% end
% fclose(fid);

%% Add Bisque and JAI paths
bisque = which('bisque.jar');
jai1 = which('clibwrapper_jiio.jar');
jai2 = which('jai_codec.jar');
jai3 = which('jai_core.jar');
jai4 = which('jai_imageio.jar');

fid = fopen(clpath,'a');
fprintf(fid, '%s\n', bisque);
fprintf(fid, '%s\n', jai1);
fprintf(fid, '%s\n', jai2);
fprintf(fid, '%s\n', jai3);
fprintf(fid, '%s\n', jai4);
fclose(fid);
%%