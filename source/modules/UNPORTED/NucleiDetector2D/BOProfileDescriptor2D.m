function nucleiFilteredPositions = BOProfileDescriptor2D(imageIn, nucleiPositions, descriptorTable, cellSize, resolutionXY, scaleXY)
%% BOProfileDescriptor2D
%   Boguslaw Obara, http://boguslawobara.net/
%
%   Version:
%       0.1 - 14/11/2008 First implementation
%%
fprintf('BOProfileDescriptor2D ... \n');
%%
cellsizeXY = cellSize; 
sizeXY = cellsizeXY/resolutionXY;
distancemaxXY = round(scaleXY*sizeXY);
%% Local Analysis
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

    if (m<distancemaxXY)
        lineMask = zeros(size(imageIn));
        lineMask = func_DrawLine(lineMask, nucleiPositions_tmp(ix,1), nucleiPositions_tmp(ix,2), nucleiPositions_tmp(jx,1), nucleiPositions_tmp(jx,2), 1);
        profileLine = double(imageIn(logical(lineMask)));
        profileLength = sum(sqrt(double(1.0 + diff(profileLine).^2)));
        
%         imagesc(imageIn), colormap gray;
%         hold on 
%         plot(nucleiPositions_tmp(ix,2), nucleiPositions_tmp(ix,1), 'yo')
%         hold on          
%         plot(nucleiPositions_tmp(jx,2), nucleiPositions_tmp(jx,1), 'ro')
% %         %subplot(1,3,3),plot(profileLine, 'ro-')
%         profileLength
%         waitforbuttonpress
   
        s1 = descriptorTable(nucleiPositions_tmp(jx,3),4);        
        s2 = descriptorTable(nucleiPositions_tmp(ix,3),4);        
        if profileLength<20
            if s1<s2
                nucleiPositions_tmp(jx,:) = []; %fprintf(1,'Red color\n');
            else
                nucleiPositions_tmp(ix,:) = []; %fprintf(1,' Yellow color\n');
            end
            stopmin = 1;
        end
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