function Botanicam(mex_url, access_token, image_url,plantpart)
    % identifies speices by their leafs or a bush by a broad image of the
    % entire plant

    session = bq.Session(mex_url, access_token); 
    try
        
        %query
        if strcmp(plantpart,'bush')
            query='"Dataset":"Botanicam Model" AND "Classification Method":"Bush Descriptor"';
        elseif strcmp(plantpart,'leaf')
            query='"Dataset":"Botanicam Model" AND "Classification Method":"Leaf Descriptor"';
        end
        
        % fetch provided ROI
        roi = session.mex.findNode('//tag[@name="inputs"]/tag[@name="image_url"]/gobject[@name="roi"]/rectangle');
        if ~isempty(roi),
            rect = roi.getVertices();
            rect = rect(:,1:2);
        else
            rect = [];
        end
        
        % fetching image, require 3 channel RGB image with max size of 1024
        session.update('0% - fetching image');   
        image = session.fetch(image_url); 
        if isempty(rect),
            im = image.slice(1,1).depth(8,'d').resize(2000, 2000, 'BC', 'MX').default().fetch();
        else
            im = image.slice(1,1).depth(8,'d');
            im = im.roi(rect(1,2),rect(1,1),rect(2,2),rect(2,1));
            im = im.resize(1024, 1024, 'BC', 'MX').default().fetch();
        end
        
        % fetches query from the database
        queryurl=regexprep(query,'"','%22'); 
        queryurl=regexprep(queryurl,' ','%20');
        queryurl=regexprep(queryurl,'(','%28');
        queryurl=regexprep(queryurl,')','%29');
        data_service=[session.bisque_root,'/data_service/file?','tag_query=',queryurl,'&tag_order=@ts:asc&limit=1&wpublic=1'];
        dataset=session.fetch(data_service);

        % parces out the webpage to find the url were the files are located
        expression = '//file';
        import javax.xml.xpath.*;
        factory = XPathFactory.newInstance;
        xpath = factory.newXPath;    
        xnodes = xpath.evaluate(expression, dataset.element, XPathConstants.NODESET );
        if isempty(xnodes) || xnodes.getLength()<1,
            error('Could not find a Botanicam Model file.');
        end            
        urls = cell(xnodes.getLength(),1);
        foldername = cell(xnodes.getLength(),1);
        for i=1:xnodes.getLength(),
            urls{i} = char(xnodes.item(i-1).getAttribute('uri'));
            foldername{i} = char(xnodes.item(i-1).getAttribute('name'));
        end

        % fetching the zip file and unzipping it
        file = session.fetch([urls{end} '?view=deep']);
        file.fetch(foldername{end});
        unzip(foldername{end});
        newfoldername=foldername{end}(1:end-4);
                
        %% RUN
        % runs one of the plant identifiers as specified
        session.update('20% - recognizing');  
        if strcmp(plantpart,'bush')
                data = run_gplant_recognizer(im,newfoldername,file);
        elseif strcmp(plantpart,'leaf')
                data = run_lplant_recognizer(im,newfoldername,file);
        end
            
        %% SAVE RESULTS
        session.update('90% - storing results');
        
        %creates output session
        outputs = session.mex.addTag('outputs');
        summary = outputs.addTag('summary');
        
        % loops though the tags in the output of the plant identifier and
        % posts them accordingly
        query= [];
        for x=1:length(data)
            if iscellstr(data{x}{2})
                value=char(data{x}{2});
            else
                value=cell2mat(data{x}{2});
            end
            if strfind(value,'http://')==1
                summary.addTag(char(data{x}{1}), value,'link');
            else
                summary.addTag(char(data{x}{1}), value);
            end

	     %creates the query to show similar images 
            if isempty(query)
                query=['"',char(data{x}{1}),'":"',value,'"']; 
            else
                query=[query,' AND "',char(data{x}{1}),'":"',value,'"']; 
            end
        end
        display('finished');
             
        browser = outputs.addTag('similar_images', query, 'browser');
        % ends the session
        session.finish();
        
    catch err
        ErrorMsg = [err.message, 10, 'Stack:', 10];
        for i=1:size(err.stack,1)
            ErrorMsg = [ErrorMsg, '     ', err.stack(i,1).file, ':', num2str(err.stack(i,1).line), ':', err.stack(i,1).name, 10];
        end
        session.fail(ErrorMsg);
    end
end
    
