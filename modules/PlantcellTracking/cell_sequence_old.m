function [sequence,c] = cell_sequence(segmentedImage)

d=size(segmentedImage,3);

for j=1:d
    
    cord{j}=regionprops(bwlabeln(segmentedImage(:,:,j)),'pixellist','PixelIdxList', 'Image','FilledImage','centroid');
    %contours{j}= bwboundaries(segmentedImage(:,:,j));
    %contours{j}=cord{j}
end

for j=1:d-1
    c{j}=full_tracking2(segmentedImage(:,:,j),segmentedImage(:,:,j+1),4,4,50,1,1);
end

[ind{1},ind{2}]=find(c{1}>0);
 
noCells=length(ind{1});

for i=1:noCells
    
    s{1}=ind{1}(i);
    previous_ind=s(1);
    for ii=1:d-1
       
        for iii=1:length(previous_ind)
            p_ind=previous_ind{iii};
            for iiii=1:length(p_ind)
             index_temp{iii}=find(c{ii}(p_ind,:)>0);
            end
        end
        
        s{ii+1}=index_temp;
        previous_ind=index_temp;
        
%         if length(previous_ind)==1
%             clear index_temp;
%             index_temp=find(c{ii}(previous_ind,:)>0);
%             s{ii+1}=index_temp;
%             previous_ind=index_temp;
            
%         elseif length(previous_ind)==2
%             clear index_temp;
%             previous_ind_temp=previous_ind;
%             clear previous_ind;
%             previous_ind{1}=previous_ind_temp(1);
%              previous_ind{2}=previous_ind_temp(2);
%             index_temp{1}=find(c{ii}(previous_ind{1}{1},:)>0);
%             index_temp{2}=find(c{ii}(previous_ind{2}{1},:)>0);
% %             index_temp{1}=index_temp1;
% %             index_temp{2}=index_temp2;
%             s{ii+1}=index_temp;
%             previous_ind=index_temp;
        end
        
    end
    sequence{i}=s;
end

