function [sequence_spatial] = spatial_sequence(segmentedImage)
%sequence_spatial{i}{t} i time, t cell  
d=size(segmentedImage);

if length(d)==3   %single slice series
    d(4)=1;   
end

for i=1:d(3)
    for j=1:d(4)
        cord{i,j}=regionprops(bwlabeln(segmentedImage(:,:,i,j)),'pixellist','PixelIdxList', 'centroid');
    end
end

for i=1:d(3)-1
    for j=1:d(4)
        c{i,j}=full_tracking2_s(segmentedImage(:,:,i,j),segmentedImage(:,:,i+1,j),4,4,50,1,1);
        lineage{i,j}=lineage_structure(c{i,j});
    end
end

for t=1:d(4)%t-time point
    noCells=length(cord{1,t});
    
    for i=1:noCells %the ith cell
        s{1}=i;
        for z=2:d(3) %the z slice
            s{z}=[];
            for ii=1:length(s{z-1})
                s_temp=lineage{z-1,t}(s{z-1}(ii)).daughters;
                
                s{z}=[s{z},s_temp];
            end
        end
        sequence_spatial{i,t}=s;
    end
end


% for j=2:d-1
%     c_matrix=c{j};
%     [ind_1,ind_2]=find(c_matrix>0);
%     for jj=1:length(ind_1) %# of new cells being tracked starting from the jth time point
%         if isempty(find(c{j-1}(:,ind_1(jj))>0))==1
%             noCells=noCells+1;
%             for jjj=1:j-1
%                 s{jjj}=[];
%             end
%             s{j}=ind_1(jj);
%             for t=j+1:d %the t time
%                 s{t}=[];
%                 for ii=1:length(s{t-1})
%                     s_temp=lineage{t-1}(s{t-1}(ii)).daughters;
%                     s{t}=[s{t},s_temp];
%                 end
%             end
%             sequence{noCells}=s;
%         end
%     end
% end