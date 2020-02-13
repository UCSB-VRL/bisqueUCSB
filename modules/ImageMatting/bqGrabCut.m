function seg_fg = bqGrabCut(session, I, I_d, featChoice, noBins, nlink_sigma, interaction_cost, HARDCODE_SEEDS, USE_STROKE_DT, STROKE_VAR)

    % Auxillary Parameters
    [noRows noCols noSlices] = size(I);
    strokeMask = zeros( noRows, noCols);
    lattice_size = [noRows noCols];
    ISmooth = imfilter(I(:,:,1), fspecial('gauss', [5 5], 1.4), 'same'); 
    %vrl_visualize_interaction_map(ISmooth, nlink_sigma, 5);

    %% Feature Computation
    ISmooth = double(reshape(ISmooth, lattice_size(1) * lattice_size(2), 1));
    [edges, no_nlinks] = vrl_Construct2DLattice(lattice_size,1);
    
    if( strcmp( featChoice, 'GRAY_HISTOGRAM' ) )
        fgHist = vrl_grayhist(I, I_d{1}, noBins);
        bgHist = vrl_grayhist(I, I_d{2}, noBins);
        fgndProject = vrl_grayhistbp(I, fgHist); likMaps{1} = fgndProject;
        bgndProject = vrl_grayhistbp(I, bgHist); likMaps{2} = bgndProject;
    elseif( strcmp( featChoice, 'COLOR_HISTOGRAM' ) )
        if( noSlices ~= 3 )
            error('Algorithm works only on 3 channel data');
        end
        fgHist = vrl_colorhist(I, I_d{1}, noBins);
        bgHist = vrl_colorhist(I, I_d{2}, noBins);
        fgndProject = vrl_colorhistbp(I, fgHist ); likMaps{1} = fgndProject;
        bgndProject = vrl_colorhistbp(I, bgHist ); likMaps{2} = bgndProject;
    elseif( strcmp( featChoice, 'TEXTURE_HISTOGRAM' ) )
        [temp1 fgHist] = vrl_msPatchHist(I, I_d{1}, noBins);
        [temp2 bgHist] = vrl_msPatchHist(I, I_d{2}, noBins);
        fgndProject = vrl_msPatchHistbp(I, fgHist); likMaps{1} = fgndProject;
        bgndProject = vrl_msPatchHistbp(I, bgHist); likMaps{2} = bgndProject;
    else
        display('Unknown Feature');
    end

    % If using Distance Transforms for Locality Sensitive Segmentation
    if( USE_STROKE_DT )
        strokeMask( I_d{1} ) = 255; strokeDT = exp( -bwdist(strokeMask) / STROKE_VAR );
        fgndProject = fgndProject .* (strokeDT);
        bgndProject = bgndProject .* (1-strokeDT);
    end

    fgndProject = -log( fgndProject + 0.01 );
    bgndProject = -log( bgndProject + 0.01 );

    % HardCode Potentials
    if( HARDCODE_SEEDS )
        fgndProject( I_d{2} ) = 10^6;
        bgndProject( I_d{1} ) = 10^6;
    end

    [weights,w_dist] = vrl_edgeweight(edges,ISmooth',lattice_size, nlink_sigma);
    [seg_fg] =  reshape( vrl_gc( int32([2, lattice_size(1) * lattice_size(2), no_nlinks]), ...
                double([fgndProject(:) bgndProject(:)]'), ...
                [edges-1, interaction_cost * weights]' ...
                ) , lattice_size(1), lattice_size(2) );
end