function nucleiFilteredPositions = BOStatDescriptor2D(imageIn, nucleiPositions, descriptorTable, cellSize, resolutionXY, scaleXY )
%% BOStatDescriptor2D - calculate Statistical descriptor
% 
%   Boguslaw Obara, http://boguslawobara.net/
%
%   Version:
%       0.1 - 14/09/2007 First implementation
%%
fprintf('BOStatDescriptor2D ... \n');
%% Setting the kernel and mask size
cellsizeXY = cellSize;
sizeXY = cellsizeXY/resolutionXY;
distancemaxXY = round(scaleXY*sizeXY);

nucleiPositions_tmp = nucleiPositions;
tableSize = size(nucleiPositions_tmp,1);
stop = 1; stopmin = 0; j = 1;
while(stop>0)
    ix = 1;
    if j>tableSize
        break;
    end
    m = 10000000;
    for i=1:tableSize
        if i~=j 
            d = sqrt( (nucleiPositions_tmp(i,1) - nucleiPositions_tmp(j,1))^2 + (nucleiPositions_tmp(i,2) - nucleiPositions_tmp(j,2))^2 );
            if m > d
                m = d; ix = i; jx = j;
            end
        end
    end

%         imagesc(imageIn), colormap gray;
%         hold on 
%         plot(nucleiPositions_tmp(ix,2), nucleiPositions_tmp(ix,1), 'yo')
%         hold on          
%         plot(nucleiPositions_tmp(jx,2), nucleiPositions_tmp(jx,1), 'ro')
%         %subplot(1,3,3),plot(profileLine, 'ro-')
        
    
    if (m<distancemaxXY)
        s1 = descriptorTable(nucleiPositions_tmp(jx,3),4);        
        s2 = descriptorTable(nucleiPositions_tmp(ix,3),4);        
        if s1<s2
            nucleiPositions_tmp(jx,:) = []; %fprintf(1,'Red color\n');
        else
            nucleiPositions_tmp(ix,:) = []; %fprintf(1,' Yellow color\n');
        end
        stopmin = 1;
        tableSize = size(nucleiPositions_tmp,1);     

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
nucleiFilteredPositions = sortrows(nucleiFilteredPositions, 3);
end
%%
