% [output, info] = bq.connect(method, url, location, input, user, password)
%
% Lowest level communication function that can do HTTP requests
%
% INPUT:
%   method   - HTTP method: GET/POST/PUT/DELETE
%   url      - url to fetch, may contain authentication which will be
%               stripped and sent in the HTTP header:
%               * Basic Auth - http://user:pass@host/path
%               * Bisque Mex - http://Mex:IIII@host/path
%   location - optional: file path to where to store fetched bytes, 
%                give [] if no file should be written but user/pass is req
%   input    - optional: stream to send to the server
%                give [] if no file should be written but user/pass is req
%   user     - optional: string with user name
%   password - optional: string with user password
%
% OUTPUT:
%    output - either byte vector or a file name if location was given 
%    info   - struct with HTTP return code and error string
%
% REQUIREMENTS:
%    For all practical purpouses you need an increased JVM heap
%    in order to get all the commmunication functionality going smoothly 
%    you should increase those settings by copying the file java.opts
%    to your matlab location:
%        MATLAB/YOUR-VERSION/bin/YOUR-ARCH/
%    where:
%        YOUR-VERSION will be something like R2009b, R2011a, ect...
%        YOUR-ARCH may be something like win64
%
% EXAMPLES:
%   s = bq.get('http://user:pass@host/path');
%   [s, info] = bq.get('http://host/path', [], 'user', 'pass');
%   [f, info] = bq.get('http://user:pass@host/path', 'myfile.xml');
%
% AUTHOR:
%   Dmitry Fedorov, www.dimin.net
%
% VERSION:
%   0.1 - 2011-06-27 First implementation
%

function [output, info] = post_mpform(url, input, user, password)
    if ~exist('url', 'var') error(message('BQ.post_mpform:RequiresUrl')); end
    if ~exist('input', 'var') error(message('BQ.post_mpform:RequiresInput')); end
    
    % This function requires Java
    if ~usejava('jvm')
       error(message('BQ.connect:NoJvm'));
    end

    import java.io.IOException;
    import java.io.FileInputStream;
    import java.io.BufferedInputStream;
    import java.io.BufferedOutputStream;    
    import java.io.File;      
    % Be sure the proxy settings are set.
    %import com.mathworks.mlwidgets.io.InterruptibleStreamCopier;
    com.mathworks.mlwidgets.html.HTMLPrefs.setProxySettings;
    
    % extract user name-password or Mex auth from the given in the URL
    % url = 'http://UUU:PPP@host.edu/images/1234';
    % url = 'https://Mex:IIII@host.edu/images/1234';
    url = bq.Url(url);
    if url.hasCredentials(),
        user = url.getUser();
        password = url.getPassword();
        url.setUser([]);
        url.setPassword([]);        
    end    
    
    % Matlab's urlread() doesn't do HTTP Request params, so work directly with Java
    % old way
    %server = java.net.URL(url);
    %connection = server.openConnection();
    
    % new: begin
    handler = [];
    switch url.getScheme()
        case 'https'
            try
                handler = sun.net.www.protocol.https.Handler;
            catch exception %#ok
                handler = [];
            end
    end

    try
        if isempty(handler)
            server = java.net.URL(url.toString());
        else
            server = java.net.URL([], url.toString(), handler);
        end
    catch exception
        error(message('BQ.connect:Server Cannot init'));
    end

    % Get the proxy information using MathWorks facilities for unified proxy
    % prefence settings.
    mwtcp = com.mathworks.net.transport.MWTransportClientPropertiesFactory.create();
    proxy = mwtcp.getProxy(); 

    % Open a connection to the URL.
    if isempty(proxy)
        connection = server.openConnection;
    else
        connection = server.openConnection(proxy);
    end    
    % new: end    
    
    boundary = ['----BisqueMatlabAPIBoundary' randomstring(20)];
    connection.setReadTimeout(1200000);
    connection.setRequestMethod('POST');
    connection.setRequestProperty('Connection', 'Keep-Alive');
    connection.setRequestProperty('Content-Type', ['multipart/form-data; boundary=',boundary]);      
    connection.setDoInput(true);
    connection.setDoOutput(true);
    connection.setUseCaches(false);        

    if exist('user', 'var') && exist('password', 'var') && ...
       ~isempty(user) && ~isempty(password),
        if ~strcmpi(user, 'Mex') ,
          connection.setRequestProperty('Authorization', ['Basic ' base64encode([user ':' password])]);
        else
          connection.setRequestProperty('Mex', password);
        end
    end
  
    % construct body parts
    eol = [char(13),char(10)];    
    [~, name, ext] = fileparts(input);
    filename = [name ext];
    
    file_length = 0;
    if ischar(input),
        file_length = getfilesize(input);
    else
        file_length = length(input);
    end      
    
    
    initial = [eol];
%     initial = [initial, '--', boundary, eol];
%     initial = [initial, 'Content-Disposition: form-data; name="file_tags"', eol];
%     initial = [initial, eol];
%     initial = [initial, '<resource type="file" name="', filename,'" uri="', filename,'" />', eol];    
    
    initial = [initial, '--', boundary, eol];
    initial = [initial, 'Content-Disposition: form-data; name="file"; filename="', filename,'"', eol];
    %initial = [initial, 'Content-Length: ',int2str(file_length), eol]; % dima: this creates incorrect file!
    initial = [initial, 'Content-Type: application/octet-stream', eol];
    initial = [initial, eol];
       
    final = [eol, '--', boundary, '--', eol]; 
    
    content_length = length(initial) + length(final) + file_length;
    connection.setRequestProperty('Content-Length', int2str(content_length)); 
    connection.connect();  
    
    % write body out
    out = java.io.BufferedOutputStream(connection.getOutputStream());
    outp = java.io.PrintStream(connection.getOutputStream); % stream for textual output

    outp.print(initial);
    % write actual payload
    if ischar(input),
        file2stream(out, input);
        out.flush();
    else
        %out.write(input); % if the input is a vector
    end    
    outp.print(final);
    outp.close;    
    out.close; 
    
    info.status  = connection.getResponseCode();
    info.error = char(readstream(connection.getErrorStream()));

    if info.status>=300,
        output = [];
        error(['bq.post_mpform:error\nStatus: ' int2str(info.status) '\nMethod: POST\nURL: ' url.toString() '\nError:\n' info.error], '');
    %elseif exist('location', 'var') && ~isempty(location),    
    %    output = stream2file(connection.getInputStream(), location);        
    %    %output = stream2file( java.io.BufferedInputStream(connection.getInputStream(), 4*1024), location);
    else
        output = readstream(connection.getInputStream());
        %output = readstream( java.io.BufferedInputStream(connection.getInputStream(), 4*1024) );
    end
end

function out = base64encode(str)
    % Uses Sun-specific class, but we know that is the JVM Matlab ships with
    encoder = sun.misc.BASE64Encoder();
    out = char(encoder.encode(java.lang.String(str).getBytes()));
end

function str = randomstring(N)
    myset = char(['A':'Z' 'a':'z' '0':'9']);
    i = ceil(length(myset)*rand(1,N));
    str = myset(i);
end

function output = readstream(inputStream)
    output = [];
    if isempty(inputStream), return; end
        
    %READSTREAM Read all bytes from stream to uint8
    try
        import com.mathworks.mlwidgets.io.InterruptibleStreamCopier;
        byteStream = java.io.ByteArrayOutputStream();
        isc = InterruptibleStreamCopier.getInterruptibleStreamCopier();
        isc.copyStream(inputStream, byteStream);
        inputStream.close();
        byteStream.close();
        output = typecast(byteStream.toByteArray', 'uint8'); %'
    catch err,
        error('bq.get:StreamCopyFailed', 'Error while downloading URL. Your JVM might not have enough heap memory...');        
    end
end

function file2stream(output, location)
    input = java.io.BufferedInputStream(java.io.FileInputStream(location));
    try
        import com.mathworks.mlwidgets.io.InterruptibleStreamCopier;
        isc = InterruptibleStreamCopier.getInterruptibleStreamCopier();
        isc.copyStream(input, output);        
        %output.close; % dima: should not be closed yet, other multipart
        %from data is written
        input.close;
    catch err,
        input.close;
        error('bq.post_mpform.file2stream', ['Error while reading file stream: ' err.message]);
    end
end

function fileSize = getfilesize(fileName)
    fileSize = 0;
    dirStruct = dir(fileName);
    if ~isempty(dirStruct),
        fileSize = dirStruct.bytes;
    end
end
