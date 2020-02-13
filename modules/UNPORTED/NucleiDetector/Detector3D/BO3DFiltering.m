function nucleiFilteredPositions = BONucleiDetector3DFiltering(imageIn, nucleiPositions, cellSizeXY, cellSizeZ)

%% Local Analysis
if ~exist('cellSizeXY','var')
    distancemaxXY = 25;
else
    distancemaxXY = cellSizeXY;
end
if ~exist('cellSizeZ','var')
    distancemaxZ = 25;
else
    distancemaxZ = cellSizeZ;
end
% distancemaxXY = 25;
% distancemaxZ = 3;
nucleiPositions_tmp = nucleiPositions;
%figure,
%for j=size(nucleiPositions_tmp,1):-1:1
tableSize = size(nucleiPositions_tmp,1);
for j=1:tableSize
    ix = 1;
    if j>tableSize
        break;
    end
    m = 10000000;
    for i=1:tableSize
        if i~=j 
            d = sqrt( (nucleiPositions_tmp(i,1) - nucleiPositions_tmp(j,1))^2 + (nucleiPositions_tmp(i,2) - nucleiPositions_tmp(j,2))^2 + (nucleiPositions_tmp(i,3) - nucleiPositions_tmp(j,3))^2 );
            if m > d
                m = d; ix = i; jx = j;
            end
        end
    end
    if (m<distancemaxXY) && (abs(nucleiPositions_tmp(ix,3)- nucleiPositions_tmp(jx,3))<=distancemaxZ)
%         subplot(2,2,1),imagesc(imageIn(:,:,nucleiPositions_tmp(ix,3))), colormap gray;
%         hold on
%         plot(nucleiPositions_tmp(ix,2), nucleiPositions_tmp(ix,1), 'wo')
%         title(nucleiPositions_tmp(ix,3))
% 
%         subplot(2,2,2),imagesc(imageIn(:,:,nucleiPositions_tmp(jx,3))), colormap gray;
%         hold on
%         plot(nucleiPositions_tmp(jx,2), nucleiPositions_tmp(jx,1), 'yo')
%         title(nucleiPositions_tmp(jx,3))
% 
%         subplot(2,2,3),imagesc(imageIn(:,:,nucleiPositions_tmp(jx,3))), colormap gray;
%         hold on
%         plot(nucleiPositions_tmp(ix,2), nucleiPositions_tmp(ix,1), 'wo')
%         hold on
%         plot(nucleiPositions_tmp(jx,2), nucleiPositions_tmp(jx,1), 'yo')
%         hold on
        %[m  abs(nucleiPositions(ix,3)- nucleiPositions(jx,3))]
        %distanceMaxValue = round(m*0.75); %0.75
        distanceMaxValue = round(distancemaxXY*0.75);
        [imageInMask1 valuesInMask1]= createMask3D(imageIn, nucleiPositions_tmp(jx,1), nucleiPositions_tmp(jx,2), nucleiPositions_tmp(jx,3), distanceMaxValue, 1);        
        [imageInMask2 valuesInMask2]= createMask3D(imageIn, nucleiPositions_tmp(ix,1), nucleiPositions_tmp(ix,2), nucleiPositions_tmp(ix,3), distanceMaxValue, 1);        
        valuesInMask1 = double(valuesInMask1)/double(max(valuesInMask1(:)));
        valuesInMask2 = double(valuesInMask2)/double(max(valuesInMask2(:)));
        v1 = var(double(valuesInMask1(:)));
        v2 = var(double(valuesInMask2(:)));
        m1 = mean(double(valuesInMask1(:)));
        m2 = mean(double(valuesInMask2(:)));        
%% Remove 
        flagGoodW=0;
        flagGoodY=0;        
%         subplot(2,2,4),imagesc(imageIn(:,:,nucleiPositions_tmp(jx,3))), colormap gray;
%         hold on
        if v1>v2% || m1>m2
%             plot(nucleiPositions_tmp(ix,2), nucleiPositions_tmp(ix,1), 'wo')
            nucleiPositions_tmp(jx,:) = [];
            flagGoodY=1;
        else
%             plot(nucleiPositions_tmp(jx,2), nucleiPositions_tmp(jx,1), 'yo')
            nucleiPositions_tmp(ix,:) = [];
            flagGoodW=1;
        end

        %fprintf(1,'White color:  var1:%.4f  m1:%.4f flag:%d \nYellow color:  var2:%.4f  m2:%.4f flag:%d \n\n', v1, m1, flagGoodW, v2, m2, flagGoodY);        
        tableSize = size(nucleiPositions_tmp,1);
    %waitforbuttonpress
    end
end    
nucleiFilteredPositions = nucleiPositions_tmp;
nucleiFilteredPositions = sortrows(nucleiFilteredPositions, 4);
end