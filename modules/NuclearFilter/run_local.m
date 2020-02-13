function run_local(filename, nuclear_channel, nuclear_diameter, varargin)
     
    [imn, ~, res] = bim.read_stack_ch(filename, nuclear_channel); 
       
    %% Run
    ns =  (nuclear_diameter/2.0) ./ [res.y res.x res.z];

    fim = enhance3d(imn, ns(1:3));   
        
    bim.write_ome_tiff( fim, 'filtered.ome.tif', struct('z', 0), struct('x', res.x, 'y', res.y, 'z', res.z));
end