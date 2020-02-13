function [I, contours, polyline] = MicrotubuleTracker(mex_url, access_token, image_url)

    % Initialize BISQUE session
    session = bq.Session(mex_url, access_token);
    session.update('Fetching image.');
    
    image = session.fetch(image_url);
    I = image.fetch();
    
    % Parse the polylines vertices.
    polylines = session.mex.findNode('//tag[@name="inputs"]/tag[@name="resource_url"]/gobject[@name="initialTrace"]/polyline');
    [noRows noCols noSlices] = size(I);

    polyline = polylines.getVertices();
    
    session.update('Working...');
    [frameEnd, contours] = MainModuleNew(I, fliplr(polyline(:,1:2)), 1, session);
    
    session.update('Collecting results.');
    % create an output tag which would contain all the output information
    outputs = session.mex.addTag('outputs');

    % Store segmented object's contour back on the mex
    imref = outputs.addTag('Microtubule image', image_url, 'image'); 
    sObject = imref.addGobject('Object', 'Microtubule');
    
    for i = 1 : size(contours, 1)
        sObject.addGobject('polyline', sprintf('Trace %d', i), [contours{i}  repmat([1 i], [size(contours{i},1) 1])]);
    end

    session.update('Saving results.');
    session.finish();
    
end