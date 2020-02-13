function nucleiFilteredPositions = BO3DStatDescriptor(imageIn, nucleiPositions, descriptorTable, cellSize, resolutionXY, resolutionZ, scaleXY, scaleZ )
% clear all; close all; clc;
% %% Load data
%load('data/imageIn2');
%im_green = im_green(:,:,1:14);
% im_red = im_red(:,:,1:14);
% imageIn2 = im_green;
% imageIn = im_red;
% load('data/nucleiDescriptorTable2');
% 
% %% Plot errors
% %load('data/nucleiPositionsGT');
% %load('data/nucleiPositions');
%load('data/nucleiPositionsMore');
%nucleiPositions(:,4) = (1:size(nucleiPositions,1))';
% 
% load('data/nucleiDescriptorTable2');
fprintf('BO3DStatDescriptor ... \n');
%% Local Analysis
if ~exist('cellSize','var')
    cellSize = 3.4;
end
% resolutionXY = 0.138661;
% resolutionZ = 1;
% scaleXY = 1.0;
% scaleZ = 1.0;

factorZ = resolutionZ/resolutionXY;
cellsizeXY = cellSize;
cellsizeZ = cellSize;
sizeXY = cellsizeXY/resolutionXY;
sizeZ = cellsizeZ/resolutionZ;
distancemaxXY = round(scaleXY*sizeXY);
distancemaxZ = round(scaleZ*sizeZ);

% if ~exist('cellSizeXY','var')
%     distancemaxXY = 25;
% else
%     distancemaxXY = cellSizeXY;
% end
% if ~exist('cellSizeZ','var')
%     distancemaxZ = 3;
% else
%     distancemaxZ = cellSizeZ;
% end


% distancemaxXY = 25;
% distancemaxZ = 3;
nucleiPositions_tmp = nucleiPositions;
%figure,
%for j=size(nucleiPositions_tmp,1):-1:1
tableSize = size(nucleiPositions_tmp,1);


% imageMax = imageIn(:,:,1);
% for k=2:size(imageIn,3)
%     imageMax = max(imageMax, imageIn(:,:,k));
% end

stop = 1;
stopmin = 0;
j = 1;
while(stop>0)
%for j=1:tableSize

    ix = 1;
    if j>tableSize
        break;
    end
    m = 10000000;
    for i=1:tableSize
        if i~=j 
            %if ((nucleiPositions_tmp(j,2)==232)||(nucleiPositions_tmp(j,2)==221))&&((nucleiPositions_tmp(i,2)==232)||(nucleiPositions_tmp(i,2)==221))
            %    q=3;
            %end
            d = sqrt( (nucleiPositions_tmp(i,1) - nucleiPositions_tmp(j,1))^2 + (nucleiPositions_tmp(i,2) - nucleiPositions_tmp(j,2))^2 + (factorZ*nucleiPositions_tmp(i,3) - factorZ*nucleiPositions_tmp(j,3))^2 );
            if m > d
                m = d; ix = i; jx = j;
            end
        end
    end

    d = sqrt( (nucleiPositions_tmp(ix,1) - nucleiPositions_tmp(jx,1))^2 + (nucleiPositions_tmp(ix,2) - nucleiPositions_tmp(jx,2))^2 + (nucleiPositions_tmp(ix,3) - nucleiPositions_tmp(jx,3))^2 );
    if(nucleiPositions_tmp(ix,2)==261)||(nucleiPositions_tmp(jx,2)==261)
        q=3;
    end

    if (m<distancemaxXY) && (abs(nucleiPositions_tmp(ix,3)- nucleiPositions_tmp(jx,3))<=distancemaxZ)
        
%         subplot(1,3,1), imagesc(imageIn(:,:,nucleiPositions_tmp(ix,3))), colormap gray;
%         hold on 
%         plot(nucleiPositions_tmp(ix,2), nucleiPositions_tmp(ix,1), 'yo')
%         hold on          
%         plot(nucleiPositions_tmp(jx,2), nucleiPositions_tmp(jx,1), 'ro')
%         hold on
%         title(['z: ', num2str(nucleiPositions_tmp(ix,3)),', ' , num2str(nucleiPositions_tmp(jx,3))])
% 
%         subplot(1,3,2), imagesc(imageIn2(:,:,nucleiPositions_tmp(ix,3))), colormap gray;
%         hold on 
%         hold on 
%         plot(nucleiPositions_tmp(ix,2), nucleiPositions_tmp(ix,1), 'yo')
%         hold on          
%         plot(nucleiPositions_tmp(jx,2), nucleiPositions_tmp(jx,1), 'ro')
%         hold on
%         title(['z: ', num2str(nucleiPositions_tmp(ix,3)),', ' , num2str(nucleiPositions_tmp(jx,3))])
        
%         subplot(1,3,2), imagesc(imageIn2(:,:,nucleiPositions_tmp(ix,3))), colormap gray;
%         hold on 
%         plot(nucleiPositions_tmp(ix,2), nucleiPositions_tmp(ix,1), 'yo')
%         hold on          
%         plot(nucleiPositions_tmp(jx,2), nucleiPositions_tmp(jx,1), 'ro')
%         hold on
%         title(['z: ', num2str(nucleiPositions_tmp(ix,3)),', ' , num2str(nucleiPositions_tmp(jx,3))])
        
        m1 = descriptorTable(nucleiPositions_tmp(jx,4),1);
        m2 = descriptorTable(nucleiPositions_tmp(ix,4),1);
        v1 = descriptorTable(nucleiPositions_tmp(jx,4),2);        
        v2 = descriptorTable(nucleiPositions_tmp(ix,4),2);        
        sd1 = descriptorTable(nucleiPositions_tmp(jx,4),3);        
        sd2 = descriptorTable(nucleiPositions_tmp(ix,4),3);        
        s1 = descriptorTable(nucleiPositions_tmp(jx,4),4);        
        s2 = descriptorTable(nucleiPositions_tmp(ix,4),4);        
        %p = [m1, m2; v1, v2; sd1, sd2; s1, s2]
        %if v1>v2 || s1>s2
        if s1<s2
            nucleiPositions_tmp(jx,:) = []; %fprintf(1,'Red color\n');
        else
            nucleiPositions_tmp(ix,:) = []; %fprintf(1,' Yellow color\n');
        end
        stopmin = 1;
        %fprintf(1,'Yellow color:  var1:%.4f  m1:%.4f flag:%d \nRed color:  var2:%.4f  m2:%.4f flag:%d\nProfile:%.4f\n\n', v1, m1, flagGoodY, v2, m2, flagGoodR, profileLength);        
        tableSize = size(nucleiPositions_tmp,1);     
        %waitforbuttonpress

    end
    j = j + 1;
    if j>tableSize
        if stopmin>0
            stopmin = 0;
            j = 1;
        else
            stop = 0;
        end
    end
end
nucleiFilteredPositions = nucleiPositions_tmp;
nucleiFilteredPositions = sortrows(nucleiFilteredPositions, 4);


% for j = 1:size(imageIn,3)
%     figure,imagesc(imageIn(:,:,j)), colormap gray;
%     hold on
%     for i=1:size(nucleiFilteredPositions,1)
%         if nucleiFilteredPositions(i,3)==j
%              plot(nucleiFilteredPositions(i,2), nucleiFilteredPositions(i,1), 'yo')         
%              %text(nucleiFilteredPositions(i,2), nucleiFilteredPositions(i,1), num2str(i), 'Color', 'w');
%              hold on
%         end
%     end
% end



% color = jet(size(imageIn,3));
% figure, imagesc(zeros(size(imageIn(:,:,1)),class(imageIn(:,:,1)))), colormap(color);
% im_max=zeros(size(imageIn(:,:,1)), class(imageIn(:,:,1)));
% for j = 1:size(imageIn,3)
%     im_max = max(imageIn(:,:,j),im_max);
% end
% figure,imagesc(im_max), colormap gray;
% hold on
% for i=1:size(nucleiFilteredPositions,1)
%     if nucleiFilteredPositions(i,3)==j
%          plot(nucleiFilteredPositions(i,2), nucleiFilteredPositions(i,1), 'ko', 'MarkerFaceColor', color(nucleiFilteredPositions(i,3),:))
%          hold on
%     end
% end

end
%%
