function roiHog = vrl_hog(Ix, Iy, I_roi, numBins)

%% Compute HoG for a specific superpixel
binSpacer = linspace(0, 360, numBins);
mag = sqrt( Ix( I_roi ).^2 + Iy( I_roi ).^2 );
ang = atan2( Iy( I_roi ), Ix(I_roi) ) * (180 / pi);
ang( ang < 0 ) = ang( ang < 0 ) + 360;

for iter = 1:numel(binSpacer)-1
    sel = mag( ang > binSpacer(iter) & ang < binSpacer(iter+1) );
    if( ~isempty(sel) )
        roiHog(iter) = sum( sel );
    else
        roiHog(iter) = 0;
    end
end