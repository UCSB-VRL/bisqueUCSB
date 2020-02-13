function run_local(filename, nuclear_channel, nuclear_diameter, varargin)
     
    [imn, ~, res] = bim.read_stack_ch(filename, nuclear_channel); 
       
    %% Run
    ns =  (nuclear_diameter/2.0) ./ [res.y res.x res.z];

    t = 0.025:0.025:0.5;
    if isinteger(imn),
       t = t * double(intmax(class(imn)));
    end

    np = BONuclearDetector3D(imn, ns(1:3), t);   
        
    %% Store results
    outputs = bq.Factory.new('tag', 'outputs');

    imref = outputs.addTag('MyImage', filename, 'image'); 
    g = imref.addGobject('nuclear_centroids', 'nuclear_centroids');

    for i=1:size(np,1),       
        n = g.addGobject('nucleus', int2str(i));        
        v = np(i,1:3);
        p = n.addGobject('point', 'centroid', v );
        p.addTag('confidence', np(i,5)*100, 'number'); 
    end

    outputs.save([filename '.xml']);     
end