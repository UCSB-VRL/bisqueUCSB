function WatershedSegmentation2(filename, outputs)
    r = regexp(filename,'\.','split');
    filenamexml = [r{1} '.xml'];

    image = bq.Factory.fetch(filenamexml);

    gobs = image.findNodes('//gobject/point[@name="Centroid"]/..');    
    types = cell(length(gobs),1);
    for i=1:length(types),
        types{i} = gobs{i}.getAttribute('type');
    end    
    
    points = image.findNodes('//gobject/point[@name="Centroid"]');
    anno = zeros(length(points), 2);
    for i=1:length(points),
        v = points{i}.getVertices();
        anno(i,:) = [v(2) v(1)];
    end

    if size(anno, 1)<=0, % only run segmentation if there are any inputs
        fprintf('skipping...\n'); drawnow('update');
        return;
    end

    im = imread(filename);
    hdint = vision.Deinterlacer;
    im = step(hdint, im);    
    cs = seg(im, round(anno));

    %% Store results
    fn = regexp(filename,'/','split');
    output = outputs.addTag('image', fn{end} );

    for i=1:length(cs), 
        g = output.addGobject(types{i}, types{i});
        g.addGobject('point', 'centroid', [anno(i,2), anno(i,1)] );
        c = cs{i};
        for j=1:length(c),              
            v = c{j};
            name = sprintf('contour-%d', j);
            g.addGobject('polygon', name, v );
        end
    end
    
end