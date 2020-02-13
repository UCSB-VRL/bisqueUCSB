function WatershedSegmentation(mex_url, access_token, varargin)
    session = bq.Session(mex_url, access_token);
    try
        image_url = session.mex.findValue('//tag[@name="inputs"]/tag[@name="resource_url"]');   
        
        session.update('0% - fetching image');   
        image = session.fetch([image_url '?view=deep']);        
        im = image.slice(1,1).depth(8, 'd').command('deinterlace', '').fetch();
        
        if isempty(im),
            fprintf('Failed to fetch image: %s\n', image_url);
            return;
        end

        points = session.mex.findNodes('//tag[@name="inputs"]/tag[@name="resource_url"]/gobject[@name="centroids"]/point');
        if length(points)<1,
            xpath = session.mex.findValue('//tag[@name="inputs"]/tag[@name="xpath"]', '//point[@name="Centroid"]');  
            points = image.findNodes(xpath);            
        end
        
        anno = zeros(length(points), 2);
        for i=1:length(points),
            v = points{i}.getVertices();
            anno(i,:) = [v(2) v(1)];
        end
        
        if size(anno, 1)>0, % only run segmentation if there are any inputs
            session.update('10% - segmenting'); 
            cs = seg(im, round(anno));
        else
            cs = {};
        end
        
        %% Store results
        session.update('90% - storing results');    
        outputs = session.mex.addTag('outputs');

        imref = outputs.addTag('MyImage', image_url, 'image'); 
        g = imref.addGobject('contours', 'contours');

        for i=1:length(cs), 
            c = cs{i};
            for j=1:length(c),              
                v = c{j};
                name = sprintf('contour-%d-%d', i, j);
                g.addGobject('polygon', name, v );
            end
        end

        session.finish();
     catch err
         ErrorMsg = [err.message, 10, 'Stack:', 10];
         for i=1:size(err.stack,1)
             ErrorMsg = [ErrorMsg, '     ', err.stack(i,1).file, ':', num2str(err.stack(i,1).line), ':', err.stack(i,1).name, 10];
         end
         session.fail(ErrorMsg);
     end
end