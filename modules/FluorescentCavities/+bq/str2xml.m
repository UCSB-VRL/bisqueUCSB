%  str2xml - converts string into XML document  
%
%   INPUT:
%     str - string
%
%   OUTPUT:
%     doc - Document Object Model node
%
%   AUTHOR:
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       1 - 2011-03-29 First implementation 
%

function doc = str2xml(str)
    str = char(str);
    import org.xml.sax.InputSource;
    import javax.xml.parsers.*;
    import java.io.*;
    iS = InputSource();
    iS.setCharacterStream( StringReader(str) );
    try
        doc = xmlread(iS);
    catch  error
        warning(error.identifier, error.message);
        doc = [];
    end
end 
