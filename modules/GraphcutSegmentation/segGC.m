function c = segGC(I,anno)
%% Algorithm Parameters ...

if nargin == 0
    I = imread('peppers.png');
    anno = [257 196];
end

noBins = 8; % Range [4 8 16 32]
nlink_sigma = 4; % Range 4:1:15
interaction_cost = 20; % 5:5:300
% Algorithm Features
HARDCODE_SEEDS = true; % Boolean ..... always make sure user seeds are consistent with output
STROKE_VAR     = 200;   % 20:10:200 ... variance of the distance transform

% Auxillary Parameters
[noRows noCols, ~] = size(I);
lattice_size = [noRows noCols];
ISmooth = imfilter(rgb2gray(I), fspecial('gauss', [5 5], 1.4), 'same'); 
% vrl_visualize_interaction_map(ISmooth, nlink_sigma, 5);

%% annotations inputs
FG = cell(1,size(anno,1));
for i = 1 : size(anno,1)
    temp = false(noRows, noCols);
    temp(anno(i,2),anno(i,1)) = true;
    FG{i} = imdilate(temp,strel('disk',6));
end

temp = false(noRows, noCols);
% temp(1,:) = true;
% temp(end,:) = true;
% temp(:,end) = true;
% temp(:,1) = true;
tempPoint = rand(10,2);
tempPoint(:,1) = round(tempPoint(:,1)*noCols);
tempPoint(:,2) = round(tempPoint(:,2)*noRows);
tempPoint(tempPoint==0) = 1;
tempInd = sub2ind([noRows noCols],tempPoint(:,2),tempPoint(:,1));
temp(tempInd) = true;
temp = imdilate(temp,strel('disk',6));
BG = temp;

clear temp*;

%% Feature Computation
ISmooth = double(reshape(ISmooth, lattice_size(1) * lattice_size(2), 1));
[edges, no_nlinks] = utils.vrl_Construct2DLattice(lattice_size,1);

for i = 1 : size(anno,1)
    fgHist{i} = utils.vrl_colorhist(I, FG{i}, noBins);
end
bgHist = utils.vrl_colorhist(I, BG, noBins);

for i = 1 : size(anno,1)
    fgndProject{i} = utils.vrl_colorhistbp(I, fgHist{i} ); %likMaps{1} = fgndProject;
end
bgndProject = utils.vrl_colorhistbp(I, bgHist ); %likMaps{2} = bgndProject;

% If using Distance Transforms for Locality Sensitive Segmentation

for i = 1 : size(anno,1)
    strokeMask = zeros(noRows, noCols);
    strokeMask( FG{i} ) = 255; strokeDT = exp( -bwdist(strokeMask) / STROKE_VAR );
    fgndProject_new{i} = fgndProject{i} .* (strokeDT);
    bgndProject_new{i} = bgndProject .* (1-strokeDT);
end


for i = 1 : size(anno,1)
    
    fgndProject = -log( fgndProject_new{i} + 0.01 );
    bgndProject = -log( bgndProject_new{i} + 0.01 );

    % HardCode Potentials
    tempFG = false(noRows, noCols);
    tempFG(anno(i,2),anno(i,1)) = true;
    tempFG = imdilate(tempFG,strel('disk',6));
    tempBG = false(noRows, noCols);
    tempBG(1,:) = true;
    tempBG(end,:) = true;
    tempBG(:,end) = true;
    tempBG(:,1) = true;
    if( HARDCODE_SEEDS )
        fgndProject( tempBG ) = 10^6;
        bgndProject( tempFG ) = 10^6;
    end

    
    [weights,w_dist] = utils.vrl_edgeweight(edges,ISmooth',lattice_size, nlink_sigma);
    [seg_fg] =  reshape( utils.gc.vrl_gc( int32([2, lattice_size(1) * lattice_size(2), no_nlinks]), ...
                double([fgndProject(:) bgndProject(:)]'), ...
                [edges-1, interaction_cost * weights]' ...
                ) , lattice_size(1), lattice_size(2) );
%     figure(1);imshow(uint8(I)); title( ['NLINK:' num2str(nlink_sigma) 'and INTERACTION:' num2str(interaction_cost)] );
%     hold on; contour( seg_fg - .5, [0 0], 'Color', [1 0 0], 'LineWidth', 3 ); hold off; 
    
    s = sum(seg_fg(:));
    CC = bwconncomp(logical(seg_fg));
    if CC.NumObjects > 1
        ind = sub2ind([noRows noCols],anno(i,2),anno(i,1));
        for j = 1 : CC.NumObjects
            if ~ismember(ind,CC.PixelIdxList{j})
                seg_fg(CC.PixelIdxList{j}) = 0;
            end
        end
    end
    if s < 100000 && s > 0
        %figure(5); contour(temp);
        c{i} = bwboundaries(seg_fg, 8, 'noholes');
    else
%             figure(5);plot(anno(iter,1),anno(iter,2),'gs','markersize',32)
        temp = false(size(I,1),size(I,2));
        temp(anno(i,2),anno(i,1)) = true;
        temp = imdilate(temp, strel('disk',32));
        c{i} = bwboundaries(temp, 8, 'noholes');
    end
end

if nargin == 0
    figure;imshow(I); hold on;
    for i = 1 : size(anno,1)
        plot(anno(i,1),anno(i,2),'b*','markersize',11)
        for j = 1 : numel(c{i})
            plot(c{i}{j}(:,2),c{i}{j}(:,1),'r','linewidth',2)
        end
    end
end

end