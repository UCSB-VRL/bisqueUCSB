function NuclearFilter(mex_url, access_token, varargin)
    session = bq.Session(mex_url, access_token);
    try
        image_url        = session.mex.findValue('//tag[@name="inputs"]/tag[@name="resource_url"]'); 
        nuclear_channel  = str2num(session.mex.findValue('//tag[@name="inputs"]/tag[@name="nuclear_channel"]'));
        nuclear_diameter = session.mex.findValue('//tag[@name="inputs"]/tag[@name="nuclear_size"]');     
       
        t = session.mex.findNode('//tag[@name="inputs"]/tag[@name="pixel_resolution"]');
        res =  cell2mat(t.getValues('number'));
        %res = [0.439453, 0.439453, 1.0, 1.0]; % image resolution in microns per pixel
       
        image = session.fetch(image_url);        
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
        
        ns =  (nuclear_diameter/2.0) ./ res; 
        
        % tile size used for processing large images
        maxsz = [1024, 1024, 256];
        
        % max image buffer of 1GB
        maxbytes = 1024 * 1024 * 1024; 

        imgsz = [image.info.image_num_x, image.info.image_num_y, image.info.image_num_z]; 
        imgbytes = (image.info.image_pixel_depth / 8) * imgsz(1) * imgsz(2) * imgsz(3);
        step = imgsz - round(ns(1:3));        
        
        %% run detection per time point
        totalStart = tic;
        
        session.update(sprintf('0%% - fetching image'));
        fprintf('Fetching image\n');
        tic;
        current_t=1;
        slicecmd = sprintf(',,,%d', current_t);           
        imn = image.command('slice', slicecmd).remap(nuclear_channel).fetch();  
        toc

        fprintf('Filtering nuclei\n');
        tic;        
        filtered = enhance3d ( imn, ns(1:3) );
        toc        
        clearvars imn;            

        fprintf('Total processing time: %.4f seconds\n', toc(totalStart));
        

        %% Store results
        session.update('90% - storing results');
        fprintf('Storing image\n');        
        tic;        
        args = struct('filename', [image.info.filename '_filtered.ome.tif'], ...
                      'dim', struct('z', 0),...
                      'res', struct('x', res(1), 'y', res(2), 'z', res(3)) );
        fim = session.storeImage(filtered, args);        
        toc 
        
        outputs = session.mex.addTag('outputs');
        outputs.addTag('FilteredImage', fim.getAttribute('uri'), 'image'); 

        session.finish();
    catch err
        ErrorMsg = [err.message, 10, 'Stack:', 10];
        for i=1:size(err.stack,1)
            ErrorMsg = [ErrorMsg, '     ', err.stack(i,1).file, ':', num2str(err.stack(i,1).line), ':', err.stack(i,1).name, 10];
        end
        session.fail(ErrorMsg);
    end
end
