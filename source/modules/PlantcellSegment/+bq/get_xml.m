%  Downloads and parses an XML document from the Bisque system
%    doc = bq.get_xml(url, user, password)  
%
%   INPUT:
%     url      - string of the resource URL
%     user     - optional: string with user name
%     password - optional: string with user password
%
%   OUTPUT:
%       doc - Document Object Model node
%
%   AUTHOR:
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       0.1 - 2011-03-29 First implementation 
%

function doc = get_xml(url, user, password)
    error(nargchk(1,3,nargin));

    if nargin<2,
        [str, info] = bq.get(url);
    else
        [str, info] = bq.get(url, [], user, password);
    end
    
    if info.status>=300 || isempty(str),
       error('bq.get_xml:FetchingProblem', 'Error fetching data from Bisque system');
    end
    
    doc = bq.str2xml(str);
end 
