function f = get_file_list(dir_name, id)

% f = get_file_list(dir_name, id)
%
% DESC:
% Return a file list of the files wich match the regular expression id
%
% AUTHOR
% Marco Zuliani - zuliani@ece.ucsb.edu
% 
% VERSION
% 1.0
%
% INPUT:
% dir_name		= directory name
% id            = regular expression
%
% OUTPUT:
% f             = cell array file list

% example finding all tif images in a directory
% id = '\w.tif*';
% f = get_file_list(dir_name,id);

d = dir(dir_name);

l = 1;
f = {};
for h = 1:length(d)
    
    % [pathstr, name, ext, ver] = fileparts();    
    [start, finish, tokens] = regexp(d(h).name, id);
    
    if ~isempty(start) && ~isempty(finish)
        f{l} = d(h).name;
        l = l + 1;
    end;
    
end;

return