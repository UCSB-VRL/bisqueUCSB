clear; close all; clc;
addpath( genpath( 'vrl_tools/' ) );
dataPath = 'C:\researchCode\dataBase\sample_tracks\stack4\VikingFrame_';
numSlices = 100;
readData = false;
nlSigma = 8;
interactionCost = 50;

%% Read Data
if( readData )
    ctr = 1;
    for sliceIter = 1:numSlices - 1
        try,
            IStack(:,:,ctr) = adapthisteq( imresize( imread([dataPath num2str(sliceIter) '.bmp']), [512 512] ) );
            ctr = ctr + 1;
        catch me,
        end
    end
    save('data/sampleStack.mat', 'IStack');
else
    load('data/sampleStack.mat');
end

[noRows noCols numSlices] = size(IStack);
[edges, no_nlinks] = vrl_Construct2DLattice([noRows noCols],1);
max_dist = sqrt(noRows^2 + noCols^2);
% segFgPrior = roipoly(IStack(:,:,1)); save('userInit.mat', 'segFgPrior'); % save(['data/initMask' num2str(stackNum) '.mat'], 'segFgPrior');
load(['data/userInit.mat']);

for sliceIter = 1:numSlices - 1    
    %% Change variables over time
    imPrev = IStack(:,:,sliceIter);
    imCurr = IStack(:,:,sliceIter+1);
    distFg = bwdist(segFgPrior);

    %% Compute Likelihood Potential using Multi Scale Histograms
    Ifg = segFgPrior ~= 0;
    Ibg =   bwdist(segFgPrior) < sqrt(numel(Ifg)/pi) & distFg > 0; %   find(segFgPrior == 0); %
    
    [fg_proj fg_hist] = vrl_msPatchHist(imPrev, Ifg, 8);
    fgndProject = vrl_msPatchHistbp(imCurr, fg_hist);
    [bg_proj bg_hist] = vrl_msPatchHist(imPrev, Ibg, 8);
    bgndProject = vrl_msPatchHistbp(imCurr, bg_hist);
    
    %% Spatial Localizer over depth
    fgndFrac = sum(segFgPrior==1) / (sum(segFgPrior==1) + sum(segFgPrior==0) );
    expandVar = ( (1-fgndFrac) * max_dist ) / 30; % Try Learning this Offline
    fgPrior = exp( - distFg / expandVar ) ;
    bgPrior = 1 - fgPrior;
    fgPrior = adjustRange( max(fgPrior, [], 3), [0 1], [0 1]);
    bgPrior = adjustRange( min(bgPrior, [], 3), [0 1], [0 1]);
    fgPost = -log(fgndProject  .* fgPrior + 0.05);  % figure; imagesc(fgPost); return;
    bgPost = -log(bgndProject  .* bgPrior + 0.05);
    segML = fgPost<bgPost;
    % figure(302); subplot(211); imagesc(fgPost); subplot(212); imagesc(bgPost);
    
    %% Compute Edge Maps
    imSmooth = imfilter(imCurr, fspecial('gauss', [7 7], 1.2));
    im_test_smooth = double(reshape(imSmooth, noRows*noCols, 1));
    [weights,w_dist] = vrl_edgeweight(edges, im_test_smooth', [noRows noCols], nlSigma );
    
    
    %% Perform Maxflow
    segFgPrior =  reshape( vrl_gc( int32([2, noRows * noCols, no_nlinks]), ...
        double([fgPost(:) bgPost(:)]'), ...
        [edges-1, interactionCost * weights]' ...
        ) , noRows, noCols );
    
    %% Visualize Result
    figure(301); imshow(imCurr, []); hold on; contour( segFgPrior-0.5, [0 0], 'r'); hold off;
    if( numel( unique(segFgPrior) ) == 1 ), display('Not Able to Track Further, Quitting!'); break; end
    
end