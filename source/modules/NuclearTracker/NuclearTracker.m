function NuclearTracker(mex_url, access_token, varargin)
    session = bq.Session(mex_url, access_token);
    try
        session.update('0% - fetching inputs'); 
        input_mex_uri  = session.mex.findValue('//tag[@name="inputs"]/tag[@name="input_mex"]');     
        nuclear_filter = session.mex.findValue('//tag[@name="inputs"]/tag[@name="nuclear_confidence_filter"]', 0)/100.0;

        %% most inputs are in the ND3D MEX
        input_mex = session.fetch([input_mex_uri '?view=deep']);
        image_url = input_mex.findValue('//tag[@name="inputs"]/tag[@name="resource_url"]');           
        
        t = input_mex.findNode('//tag[@name="inputs"]/tag[@name="pixel_resolution"]');
        res =  cell2mat(t.getValues('number'));

        image = session.fetch([image_url '?view=deep']);        
        if isfield(image.info, 'pixel_resolution_x') && res(1)<=0,
            res(1) = image.info.pixel_resolution_x;
        end
        if isfield(image.info, 'pixel_resolution_y') && res(2)<=0,
            res(2) = image.info.pixel_resolution_y;
        end    
        if isfield(image.info, 'pixel_resolution_z') && res(3)<=0,
            res(3) = image.info.pixel_resolution_z;
        end    
        if isfield(image.info, 'pixel_resolution_t') && res(4)<=0,
            res(4) = image.info.pixel_resolution_t;
        end
        
        %% fetch centoid locations
        points      = input_mex.findNodes ('//gobject[@type="nucleus"]/point[@name="centroid"]');
        confidences = input_mex.findValues('//gobject[@type="nucleus"]/point[@name="centroid"]/tag[@name="confidence"]');        
        cm = zeros(length(points),6);
        for i=1:length(points),
            cm(i,:) = points{i}.getVertices();
            cm(i,5) = confidences{i} ./ 100.0;
        end
        cm = cm(:,1:5);
        num_t = cm(size(cm,1),4);

        centroids   = cell(num_t,1);
        confidences = cell(num_t,1);
        for i=1:num_t,
            pts = cm(cm(:,4)==i, :);
            centroids{i}   = pts(:,1:3);
            confidences{i} = pts(:,5);
        end

        resolution = zeros(num_t, 3);
        for i=1:num_t,
            resolution(i,:) = res(1:3);
        end
        
        if isempty(centroids),
            throw(MException('VerifyInput:NotEnoughElements', 'No input nuclei centorids were found...'));
        end
        
        %% running tracking
        confidencethreshold = nuclear_filter;
        session.update('10% - tracking'); 
        framematches = geometricmatch(centroids, confidences, confidencethreshold, resolution, session);

        %% creating lifelines
        lifelines = cell(length(framematches{1}),1);
        lifelines_conf = zeros(length(framematches{1}),2);

        % init lifelines
        for i=1:length(framematches{1}),
            lifelines{i} = [1, framematches{1}(i,:)];

            c1 = confidences{1}(framematches{1}(i,1));
            c2 = confidences{2}(framematches{1}(i,2));
            lifelines_conf(i, :) = [i, (c1+c2)/2.0];
        end

        % add other points
        for t=2:length(framematches)-1,
            m = framematches{t};
            for i=1:length(m),
                b = m(i,1);
                found = 0;
                for j=1:length(lifelines),
                    for k=1:size(lifelines{j},1),
                        e = lifelines{j}(k,3);
                        t2 = lifelines{j}(k,1)+1;
                        if b==e && t==t2,
                            lifelines{j} = [lifelines{j}; t, m(i,:)];

                            c1 = confidences{t}(m(i,1));
                            c2 = confidences{t+1}(m(i,2));
                            lifelines_conf(j, 2) = lifelines_conf(j, 2)+(c1+c2)/2.0;                    

                            found = 1;
                            break;
                        end
                    end
                    if found==1,
                        break;
                    end
                end
                if found==0,
                    lifelines{end+1} = [t, m(i,:)]; 

                    c1 = confidences{t}(m(i,1));
                    c2 = confidences{t+1}(m(i,2));
                    lifelines_conf(end+1, :) = [length(lifelines), (c1+c2)/2.0];            
                end
            end
        end
        
        % sort lifelines by confidence
        for i=1:length(lifelines),
            lifelines_conf(i, 2) = lifelines_conf(i, 2) / length(lifelines{i});
        end
        lifelines_conf = sortrows(lifelines_conf, 2);
        lifelines_conf = lifelines_conf(end:-1:1,:);

        lifelines2 = lifelines;
        for i=1:length(lifelines),
            lifelines{i} = lifelines2{lifelines_conf(i, 1)};
        end

        lifelines_conf(:,2) = lifelines_conf(:,2) ./ max(lifelines_conf(:,2));
        lifelines_conf(:,2) = lifelines_conf(:,2) .* 100;

        % geting matching vertices
        for i=1:length(lifelines),
            l = lifelines{i};
            lifeline = {};
            %conf = lifelines_conf(i,2);
            for j=1:size(l,1),
                t = l(j,1);
                v1 = centroids{t}(l(j,2),:); v1(3) = v1(3) + 1.5;
                v2 = centroids{t+1}(l(j,3),:); v2(3) = v2(3) + 1.5;
                lifeline{end+1,1} = [v1,t; v2,t+1;];
            end
            lifelines{i} = lifeline;
        end        
        
        
        %% creating actual lifelines from pair-wise matches
        for i=1:length(lifelines),
            matches = lifelines{i};
            lifeline = {};
            lifeline{1} = matches{1};
            for j=2:length(matches),
                m = matches{j};
                found = 0;
                for k=1:length(lifeline),
                   n = lifeline{k};
                   if n(end,1:4) == m(1,1:4),
                       found = 1;
                       lifeline{k}(end+1,:) = m(2,:);
                       break;
                   end    
                end 
                if found==0,
                    lifeline{end+1,1} = m;
                end
            end

            for j=1:length(lifeline),
                m = lifeline{j};
                n = size(m,1);
                m(:,6) = (1:n)';
                lifeline{j} = m;
            end    

            lifelines{i} = lifeline;
        end        
        
        
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        % writing results
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        
        session.update('90% - storing results');    
        outputs = session.mex.addTag('outputs');
        
        summary = outputs.addTag('summary');
        summary.addTag('Lifelines number', length(lifelines));
        
        imref = outputs.addTag('MyImage', image_url, 'image'); 
        matches = imref.addGobject('lifelines', 'lifelines');
        cc = round(hsv(length(lifelines)) .* 255);
        for i=1:length(lifelines),
            l = lifelines{i};
            color = sprintf('#%s%s%s', dec2hex(cc(i,1),2), dec2hex(cc(i,2),2), dec2hex(cc(i,3),2) );
            g = matches.addGobject('lifeline', sprintf('lifeline-%.3d', i) );
            for j=1:size(l,1),
                p = l{j};
                name = sprintf('match_%.3d', j);
                pl = g.addGobject('polyline', name, p);
                pl.addTag('color', color);
            end
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