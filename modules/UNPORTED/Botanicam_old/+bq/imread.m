% Similar to Matlab IMREAD adding HTTP authentication
%   [X, map, alpha] = bq.imread(filename)
%
% ENHANCED INPUT:
%    filename - can be a url with authentication which will be
%               stripped and sent in the HTTP header:
%               * Basic Auth - http://user:pass@host/path
%               * Bisque Mex - http://Mex:IIII@host/path
%
% EXAMPLES:
%   I = bq.imread('http://user:pass@host/path');
%
%   AUTHOR:
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       0.1 - 2011-06-27 First implementation
%

function [X, map, alpha] = imread(varargin)
    if (nargin<1)
        error('bq.imread:inputParsing', 'Too few input arguments');
    end
    
    filename = varargin{1};
    if ~ischar(filename)
        error('bq.imread:badImageSourceDatatype', ...
              'The filename or url argument must be a string.');
    end

    % Download remote file.
    if (strfind(filename, '://'))
        url = true;
        if (~usejava('jvm'))
            error('MATLAB:imread:noJava', 'Reading from a URL requires a Java Virtual Machine.')
        end
        try
            filename = bq.urlwrite(filename, tempname);
        catch %#ok<*CTCH>
            error('MATLAB:imread:readURL', 'Can''t read URL "%s".', filename);
        end
        varargin{1} = filename;
    else
        url = false;
    end

    [X, map, alpha] = imread(varargin{:});

    % Delete temporary file from Internet download.
    if (url)
        delete_download(filename);
    end
end

function delete_download(filename)
    try
        delete(filename);
    catch
        warning('MATLAB:imread:tempFileDelete', 'Can''t delete temporary file "%s".', filename)
    end
end

