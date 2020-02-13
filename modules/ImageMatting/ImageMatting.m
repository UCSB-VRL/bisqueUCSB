function segmentedImage = ImageMatting(mex_url, access_token, image_url, varargin)

    % Initialize BISQUE session
    session = bq.Session(mex_url, access_token);
    session.update('Initializing...');

    % Initialize parameters
    if (nargin < 4)
        featChoice          =   'COLOR_HISTOGRAM'; % GRAY_HISTOGRAM, COLOR_HISTOGRAM, TEXTURE_HISTOGRAM
        noBins              =   8;      % Range [4 8 16 32]
        nlink_sigma         =   7;      % Range 4:1:15
        interaction_cost    =   50;     % 5:5:300

        HARDCODE_SEEDS      =   true;   % Boolean ..... always make sure user seeds are consistent with output
        USE_STROKE_DT       =   true;   % Boolean .... for locality constrained segmentation from initial stroke
        STROKE_VAR          =   50;     % 20:10:200 ... variance of the distance transform
    else
        featChoice          =   varargin{1}; % GRAY_HISTOGRAM, COLOR_HISTOGRAM, TEXTURE_HISTOGRAM
        noBins              =   str2double(varargin{2}); % Range [4 8 16 32]
        nlink_sigma         =   str2double(varargin{3}); % Range 4:1:15   EDGE STRENGTH - control edge thickness
        interaction_cost    =   str2double(varargin{4}); % 5:5:300   weight tradeoff between region and edge cues.

        % Algorithm Features
        HARDCODE_SEEDS      =   str2num(varargin{5}); % Boolean ..... whether the user seeds should be consistent with output
        USE_STROKE_DT       =   str2num(varargin{6}); % Boolean .... foreground-stroke-locality constrained segmentation
        STROKE_VAR          =   str2num(varargin{7});   % 20:10:200 ... variance of the distance transform
    end
    
    session.update('Fetching image.');
    
    image = session.fetch(image_url);
    I = image.fetch();
    
    % Parse the polylines vertices.
    polylines = session.mex.findNodes('//tag[@name="inputs"]/tag[@name="resource_url"]/gobject[@name="stroke"]/polyline');
    [noRows noCols noSlices] = size(I);

    for regionIter = 1 : size(polylines, 1)
        polyline = bqBresenham(polylines{regionIter}.getVertices());
        I_d{regionIter} = uint64(sub2ind([noRows noCols], polyline(:,1), polyline(:,2)));
    end
    
    session.update('Working...');
    segmentedImage = bqGrabCut(session, I, I_d, featChoice, noBins, nlink_sigma, interaction_cost, HARDCODE_SEEDS, USE_STROKE_DT, STROKE_VAR);
    contours = bwboundaries(segmentedImage);
    
    session.update('Collecting results.');
    % create an output tag which would contain all the output information
    outputs = session.mex.addTag('outputs');
    
    % Store segmented object's contour back on the mex
    imref = outputs.addTag('Segmented Image', image_url, 'image'); 
    sObject = imref.addGobject('Object', 'Segmented object');
    
    for i = 1 : size(contours, 1)
        sObject.addGobject('polygon', sprintf('Boundary %d', i), contours{i}); % REMOVE -1 WHEN API STARTS DOING IT!
    end

    session.update('Saving results.');
    session.finish();
    
end

function polyline = bqBresenham(pts)
    x = [];
    y = [];
    
    for i = 1 : size(pts,1)-1
        [tx ty] = bresenham(pts(i,1),pts(i,2),pts(i+1,1),pts(i+1,2));
        x = [x;tx(1:end-1)];
        y = [y;ty(1:end-1)];
    end
    
    x = [x;pts(end,1)];
    y = [y;pts(end,2)];
    polyline = [x y];
end

%% Bresenham in Matlab courtesy Aaron Wetzler (http://www.mathworks.com/matlabcentral/fileexchange/28190-bresenham-optimized-for-matlab)
function [x y]=bresenham(x1,y1,x2,y2)
    x1=round(x1); x2=round(x2);
    y1=round(y1); y2=round(y2);
    dx=abs(x2-x1);
    dy=abs(y2-y1);
    steep=abs(dy)>abs(dx);
    if steep t=dx;dx=dy;dy=t; end

    %The main algorithm goes here.
    if dy==0 
        q=zeros(dx+1,1);
    else
        q=[0;diff(mod([floor(dx/2):-dy:-dy*dx+floor(dx/2)]',dx))>=0];
    end

    %and ends here.

    if steep
        if y1<=y2 y=[y1:y2]'; else y=[y1:-1:y2]'; end
        if x1<=x2 x=x1+cumsum(q);else x=x1-cumsum(q); end
    else
        if x1<=x2 x=[x1:x2]'; else x=[x1:-1:x2]'; end
        if y1<=y2 y=y1+cumsum(q);else y=y1-cumsum(q); end
    end
end