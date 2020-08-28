
function nuclei = analyse( Idapi, Iphf, pixel_res, nuclei, cell_size )

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % annotate nuclei locations
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    descriptor_size = round([cell_size cell_size cell_size] ./ pixel_res);
    num_nuclei = length(nuclei);
    for n=1:num_nuclei,
      [nuclei{n}.ROIdapi, nuclei{n}.ROIphf] = getVolume( Idapi, Iphf, nuclei{n}.coord, descriptor_size );
    end

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % classify
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %min_bound = MedAD(Iphf(Iphf>0));
    %min_bound = mean(Iphf(Iphf>0));
    min_bound = ( mean(Iphf(Iphf>0)) + MedAD(Iphf(Iphf>0)) ) / 2;

    nuclei = classify( nuclei, min_bound );

%     classes = [nuclei.class];
%     phf_positive = size(classes(classes>1),2);
%     fprintf('Number nuclei: %d\n', num_nuclei );
%     fprintf('PHF positive: %d\n', phf_positive );
%     fprintf('PHF positive %%: %.2f\n', (phf_positive*100)/num_nuclei );


    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % compute uncertainty
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    dapiv=[];
    phfv=[];
    for n=1:num_nuclei,
        dapiv = [ mean(nuclei{n}.ROIdapi(:)) , dapiv ];
        phfv = [ mean(nuclei{n}.ROIphf(:)) , phfv ];  
    end

    phf_vol_max = max(phfv);
    phf_vol_min = min(phfv);
    dapi_vol_max = max(dapiv);
    dapi_vol_min = min(dapiv);

    for n=1:num_nuclei,
        nuclei{n}.prob_phf  = (mean(nuclei{n}.ROIphf(:)) - phf_vol_min) / (phf_vol_max-phf_vol_min);
        nuclei{n}.prob_dapi = (mean(nuclei{n}.ROIdapi(:))) / (dapi_vol_max);
    end

end


