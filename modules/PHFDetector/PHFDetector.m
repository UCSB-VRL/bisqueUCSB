function PHFDetector(mex_url, access_token, input_mex_uri, ~, ~, ~)
    session = bq.Session(mex_url, access_token);
    try
        session.update('0% - fetching inputs'); 
        phf_channel        = str2num(session.mex.findValue('//tag[@name="inputs"]/tag[@name="phf_channel"]'));
        soma_nucleus_ratio = session.mex.findValue('//tag[@name="inputs"]/tag[@name="soma_nucleus_ratio"]');        
        nuclear_filter     = session.mex.findValue('//tag[@name="inputs"]/tag[@name="nuclear_filter_confidence"]', 0); 

        %% most inputs are in the ND3D MEX
        input_mex = session.fetch([input_mex_uri '?view=deep']);
        image_url        = input_mex.findValue('//tag[@name="inputs"]/tag[@name="resource_url"]');           
        nuclear_channel  = str2num(input_mex.findValue('//tag[@name="inputs"]/tag[@name="nuclear_channel"]'));
        nuclear_diameter = input_mex.findValue('//tag[@name="inputs"]/tag[@name="nuclear_size"]');        
        
        t = input_mex.findNode('//tag[@name="inputs"]/tag[@name="pixel_resolution"]');
        res =  cell2mat(t.getValues('number'));

        image = session.fetch([image_url '?view=deep']);        
        if isfield(image.info, 'pixel_resolution_x') && res(1)<=0,
            res(1) = getfield(image.info, 'pixel_resolution_x');
        end
        if isfield(image.info, 'pixel_resolution_y') && res(2)<=0,
            res(2) = getfield(image.info, 'pixel_resolution_y');
        end    
        if isfield(image.info, 'pixel_resolution_z') && res(3)<=0,
            res(3) = getfield(image.info, 'pixel_resolution_z');
        end    
        if isfield(image.info, 'pixel_resolution_t') && res(4)<=0,
            res(4) = getfield(image.info, 'pixel_resolution_t');
        end
        
        %% fetch ROI polygon, currently we simply look for any polygon on the image, 
        %  this is a temp measure till we have a better gobjects creater in the web
        polygon = [];
        roi = image.findNode('//polygon');
        if ~isempty(roi),
            polygon = roi.getVertices();
            %inpolygon(x,y,xv,yv);
        end;        
        
        %% fetch centoid locations
        points = input_mex.findNodes('//gobject[@type="nucleus"]/point[@name="centroid"]');
        nuclei = cell(length(points), 1);
        for n=1:length(points),
            coord = points{n}.getVertices();
            if ~isempty(polygon) && inpolygon(coord(1),coord(2),polygon(:,1),polygon(:,2))==0,
                continue;
            end
            confi = points{n}.findValue('tag[@name="confidence"]');
            if nuclear_filter>0 && confi<nuclear_filter,
                continue;
            end
            nuclei{n} = struct( 'coord', coord(1:3), 'confidence', confi );
        end
        nuclei = nuclei(~cellfun(@isempty, nuclei));
        sprintf('Number inputs:\n'); length(nuclei)
        
        if isempty(nuclei),
            throw(MException('VerifyInput:NotEnoughElements', 'No input nuclei centorids were found...'));
        end
        
        %% fetch input images
        session.update('5% - fetching input image'); 
        Idapi = image.slice([],1).remap(nuclear_channel).fetch();        
        Iphf  = image.slice([],1).remap(phf_channel).fetch();   
        
        %% classifying nuclei
        session.update('10% - classifying'); 
        cell_size = nuclear_diameter * soma_nucleus_ratio;
        nuclei = analyse( Idapi, Iphf, res(1:3), nuclei, cell_size );
        sprintf('Number classified:\n'); length(nuclei)
        
        % getting summary
        classes = [0, 0];
        for n=1:length(nuclei),
            classes(nuclei{n}.class) = classes(nuclei{n}.class) + 1;
        end        
        sprintf('Classes:\n'); classes
        
        %% Store results
        session.update('90% - storing results');    
        outputs = session.mex.addTag('outputs');
        
        summary = outputs.addTag('summary');
        summary.addTag('Count PHF+', classes(1));
        summary.addTag('Count PHF-', classes(2));
   
        imref = outputs.addTag('MyImage', image_url, 'image'); 
        g = imref.addGobject('phf_classified_centroids', 'phf_classified_centroids');
        gplus  = g.addGobject('phf_positive', 'phf_positive');
        gminus = g.addGobject('phf_negative', 'phf_negative');
        
        for j=1:length(nuclei),    
            if nuclei{j}.class == 1,
                n = gminus.addGobject('nucleus', int2str(j));
                myclass = 'PHF-';
                mycolor = '#ffffff';
            else
                n = gplus.addGobject('nucleus', int2str(j));        
                myclass = 'PHF+';
                mycolor = '#ff0000';                
            end
            p = n.addGobject('point', 'centroid', nuclei{j}.coord );
            p.addTag('confidence_nuclear', nuclei{j}.confidence, 'number'); 
            p.addTag('confidence_phf', nuclei{j}.prob_phf*100, 'number');             
            p.addTag('color', mycolor);
            p.addTag('class', myclass);            
        end
        sprintf('Results XML:\n'); outputs.toString()
        session.finish();
    catch err
        ErrorMsg = [err.message, 10, 'Stack:', 10];
        for i=1:size(err.stack,1)
            ErrorMsg = [ErrorMsg, '     ', err.stack(i,1).file, ':', num2str(err.stack(i,1).line), ':', err.stack(i,1).name, 10];
        end
        session.fail(ErrorMsg);
    end
end