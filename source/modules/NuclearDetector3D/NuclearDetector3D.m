function NuclearDetector3D(mex_url, access_token, varargin)
    session = bq.Session(mex_url, access_token);
    try
        image_url = session.mex.findValue('//tag[@name="inputs"]/tag[@name="resource_url"]');
        nuclear_channel  = str2num(session.mex.findValue('//tag[@name="inputs"]/tag[@name="nuclear_channel"]'));
        membrane_channel = str2num(session.mex.findValue('//tag[@name="inputs"]/tag[@name="membrane_channel"]', '0'));        
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
        
        % max image buffer of 512MB, double without membrane
        maxbytes = 512 * 1024 * 1024; 
        if membrane_channel<=0, 
            maxbytes = maxbytes * 2; 
        end

        % we'll aproximate large kernels by using smaller interpolated data
        % considering most imaging modailities are anisotropic and
        % usually lacking in Z resolution, thus the smaller size of max Z filter
        max_ns = [21, 21, 15];
        
        imgsz = [image.info.image_num_x, image.info.image_num_y, image.info.image_num_z]; 
        imgbytes = (image.info.image_pixel_depth / 8) * imgsz(1) * imgsz(2) * imgsz(3);
        scale = ns(1:3) ./ max_ns;
        scale(scale<1) = 1;
        if max(scale)>1, % || max(imgsz > maxsz)>0,
            newsz = round(imgsz ./ scale);
            %newsz = min(maxsz, newsz);
            imgbytes = (image.info.image_pixel_depth / 8) * newsz(1) * newsz(2) * newsz(3);
            szcmd = sprintf('%d,%d,%d,TC', newsz(1), newsz(2), newsz(3));
        else
            szcmd = [];
        end 
        step = maxsz - round(ns(1:3));        
        
        %% run detection per time point
        number_t = max(1, image.info.image_num_t);
        np = cell(number_t, 1);
        count = 0;
        for current_t=1:number_t,
            fprintf('\n\nTime %d/%d\n', current_t, number_t);
            timetext = sprintf('Time %d/%d: ', current_t, number_t);
            totalStart = tic;
            if imgbytes<=maxbytes,
                slicecmd = sprintf(',,,%d', current_t);              
                ps = detect(image, nuclear_channel, membrane_channel, slicecmd, szcmd, ns, scale, session, timetext);
            else
                % tiled processing
                ps = [];
                for x=1:step(1):imgsz(1),
                for y=1:step(2):imgsz(2),
                for z=1:step(3):imgsz(3),                
                    offset = [x, y, z];
                    to = min([x, y, z] + maxsz-1, imgsz); 
                    fprintf('\nTile [%d,%d,%d] - [%d,%d,%d]\n', ...
                        offset(1), offset(2), offset(3), to(1), to(2), to(3));
                    
                    xcmd = sprintf('%d-%d', offset(1), to(1));
                    ycmd = sprintf('%d-%d', offset(2), to(2));
                    zcmd = sprintf('%d-%d', offset(3), to(3));
                    tcmd = sprintf('%d', current_t);
                    slicecmd = sprintf('%s,%s,%s,%s', xcmd, ycmd, zcmd, tcmd);

                    if max(scale)>1,
                        newsz = round(to-offset+1 ./ scale);                     
                        szcmd = sprintf('%d,%d,%d,TC', newsz(1), newsz(2), newsz(3));
                    else
                        szcmd = [];
                    end                 

                    pss = detect(image, nuclear_channel, membrane_channel, slicecmd, szcmd, ns, scale, session, timetext);

                    pss(:,1) = pss(:,1) + offset(2)-1;
                    pss(:,2) = pss(:,2) + offset(1)-1;
                    pss(:,3) = pss(:,3) + offset(3)-1;

                    ps = [ps; pss];
                end; % z
                end; % y
                end; % x

                ps = Filter3DPointsByDescriptor(ps, ns(1:3)*1.15);
            end
            
            img_cnts = scalev(ps(:,4));
            img_mean = scalev(ps(:,5));
            feature = (5*img_cnts + 5*img_mean)/ 10; % equally weighted
            feature = scalev(feature);
            ps(:,5) = feature;
            ps = sortrows(ps, 5);            
            np{current_t} = ps;

            count = count + length(np{current_t});            
            
            fprintf('Total processing time: %.4f seconds\n', toc(totalStart));
            
            disp(ps); % debugging
            
            %fprintf('Removing temp files\n');
            %tmpnames = sprintf('8nyJ2VWWdfjf3RrkYZDiVb-bill_smith.ome.tif.0-0,0-0,*-*,%d-%d*', current_t, current_t);
            %delete(tmpnames);
        end
        
        %% Store results
        totalStart = tic;
        fprintf('Storing results\n');
        session.update('90% - storing results');    
        outputs = session.mex.addTag('outputs');
        
        summary = outputs.addTag('summary');
        summary.addTag('count', count);

        imref = outputs.addTag('MyImage', image_url, 'image'); 
        g = imref.addGobject('nuclear_centroids', 'nuclear_centroids');

        for j=1:length(np),        
            for i=1:size(np{j},1),       
                n = g.addGobject('nucleus', sprintf('%d:%d', j, i));
                v = [np{j}(i,1:3), j];
                p = n.addGobject('point', 'centroid', v );
                p.addTag('confidence', np{j}(i,5)*100, 'number'); 
            end
        end
        
        %g.save('output.xml'); % debugging 
        fprintf('Final result:\n%s', g.toString()); % debugging
        session.finish();
        fprintf('Storing time: %.4f seconds\n', toc(totalStart));
    catch err
        ErrorMsg = [err.message, 10, 'Stack:', 10];
        for i=1:size(err.stack,1)
            ErrorMsg = [ErrorMsg, '     ', err.stack(i,1).file, ':', num2str(err.stack(i,1).line), ':', err.stack(i,1).name, 10];
        end
        session.fail(ErrorMsg);
    end
end

function np = detect(image, nuclear_channel, membrane_channel, slicecmd, szcmd, ns, scale, session, timetext)
    session.update(sprintf('%s0%% - fetching image', timetext));
    fprintf('Fetching image\n');
    tic;
    if ~isempty(szcmd),
        %imn = image.slice([],current_t).remap(nuclear_channel).command('resize3d', szcmd).fetch();
        imn = image.command('slice', slicecmd).remap(nuclear_channel).command('resize3d', szcmd).fetch();
    else
        %imn = image.slice([],current_t).remap(nuclear_channel).fetch();                
        imn = image.command('slice', slicecmd).remap(nuclear_channel).fetch();  
    end

    % filter using membraine channel
    if membrane_channel>0,
        session.update(sprintf('%s5%% - fetching membrane image', timetext));
        fprintf('Fetching membrane image\n');
        if ~isempty(szcmd),                
            %imm = image.slice([],current_t).remap(membrane_channel).command('resize3d', szcmd).fetch();
            imm = image.command('slice', slicecmd).remap(membrane_channel).command('resize3d', szcmd).fetch();
        else
            %imm = image.slice([],current_t).remap(membrane_channel).fetch();
            imm = image.command('slice', slicecmd).remap(membrane_channel).fetch();  
        end
        imn = imdiff(imn, imm);
        clearvars imm;
    end
    toc
    %imn = imresize3d(imn, newsz, 'cubic');            

    %% Run
    %t = 0.025:0.025:0.5;
    t = 0.025:0.05:0.5;
    if isinteger(imn),
       t = t * double(intmax(class(imn)));
    end

    fprintf('Detecting nuclei\n');
    session.update(sprintf('%s10%% - detecting nuclei', timetext));
    sns = ns(1:3) ./ [scale(2) scale(1) scale(3)];
    pss = BONuclearDetector3D(imn, sns, t, session, timetext);
    clearvars imn;            
    pss(:,1) = pss(:,1) .* scale(2);
    pss(:,2) = pss(:,2) .* scale(1);
    pss(:,3) = pss(:,3) .* scale(3);
    np = pss;
end
