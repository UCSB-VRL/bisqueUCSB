function [segmentedImage,c] = PlantcellTracking(mex_url, access_token, image_url)

% Initialize BISQUE session
session = bq.Session(mex_url, access_token);
session.update('Initializing...');

image = session.fetch(image_url);
x=image.info.image_num_x;
y=image.info.image_num_y;
z=image.info.image_num_z;
t=image.info.image_num_t;

rois = session.mex.findNodes('//tag[@name="inputs"]/tag[@name="image_url"]/gobject[@name="roi"]/rectangle');

if ~isempty(rois),
    for len=1:length(rois)
        roi=rois{len};
        rectangle = roi.getVertices();
        rects(:,:,len) = rectangle(:,1:2);
        t_time(len)=rectangle(1,4);
        z_slice(len)=rectangle(1,3);
    end
else
    rects = [];
end;


session.update('0% - fetching image');

if isempty(rects)==1
    I= image.fetch();
    rect(1,2)=1;
    rect(1,1)=1;
    rect(2,2)=y;
    rect(2,1)=x;
    
    z_min=1;
    z_max=z;
    t_min=1;
    t_max=t;
else
    rect(1,2)=min(rects(1,2,:));
    rect(1,1)=min(rects(1,1,:));
    rect(2,2)=max(rects(2,2,:));
    rect(2,1)=max(rects(2,1,:));
    if length(t_time)==1
        t_min=1;
        t_max=t;
        z_min=1;
        z_max=z;
    else
        
        t_min=min(t_time);
        t_max=max(t_time);
        z_min=min(z_slice);
        z_max=max(z_slice);
    end
    
    I= image;
    I = I.roi(rect(1,2),rect(1,1),rect(2,2),rect(2,1));
    I = I.fetch();
    
    I=I(:,:,z_min:z_max,t_min:t_max);
end


if z==1
    I_new(:,:,1,:)=I;
elseif t==1
    I_new(:,:,:,1)=I;
else
    I_new=I;
end

session.update('Working...');
segmentedImage = watershed_seg(I_new);

session.update('Collecting results.');
% create an output tag which would contain all the output information
outputs = session.mex.addTag('outputs');

% Store segmented object's contour back on the mex
imref = outputs.addTag('Segmented Image', image_url, 'image');
sObject = imref.addGobject('Object', 'Segmented object');

d=size(segmentedImage);% d(3) is Z and d(4) is the T.

if length(d)==3   %single slice series
    d(4)=1;   
end

for i=1:d(3)%Z direction
    for j=1:d(4)% T direction
        %contours{i}{j}= bwboundaries(segmentedImage(:,:,i,j),'noholes');
        cord{i,j}=regionprops(bwlabeln(segmentedImage(:,:,i,j)),'pixellist','PixelIdxList', 'centroid');
    end
end

[sequence,c] = temporal_sequence(segmentedImage(:,:,1,:));%top slice
noCells=length(sequence);
centroid = sObject.addGobject('Object', 'Centroids');

[sequence_spatial]=spatial_sequence(segmentedImage);

for i = 1 : noCells
    pcell_t1{i} = centroid.addGobject('Tracked Cells', sprintf('Cell %d', i));
    pcelli_c{i}=pcell_t1{i}.addGobject('Centroid',sprintf('Centroid %d', i));
    ind=sequence{i};
    for t=1:d(4)
        index_topslice=ind{t};
        if isempty(index_topslice)==0
            if length(index_topslice)==1
                sequence_t=sequence_spatial{index_topslice,t};
                for z=1:d(3)
                    index=sequence_t{z};
                    if isempty(index)==0
                        cord_new=cord{z,t};
                        if length(index)==1
                            v=[cord_new(index).Centroid(2)+rect(1,1)-1,  cord_new(index).Centroid(1)+rect(1,2)-1, z+z_min-1, t+t_min-1];
                            pcelli_c{i}.addGobject('point', sprintf('cell centroid t%d', t+t_min-1), v);
                        else
                            for iii=1:length(index)
                                v=[cord_new(index(iii)).Centroid(2)+rect(1,1)-1,  cord_new(index(iii)).Centroid(1)+rect(1,2)-1, z+z_min-1, t+t_min-1];
                                pcelli_c{i}.addGobject('point', sprintf('cell centroid t%d', t+t_min-1), v);
                            end
                        end
                    end
                end
            else
                for iiii=1:length(index_topslice)%could be more than one sibling cells
                    sequence_t=sequence_spatial{index_topslice(iiii),t};
                    for z=1:d(3)
                        index=sequence_t{z};
                        if isempty(index)==0
                            cord_new=cord{z,t};
                            if length(index)==1
                                v=[cord_new(index).Centroid(2)+rect(1,1)-1,  cord_new(index).Centroid(1)+rect(1,2)-1, z+z_min-1, t+t_min-1];
                                pcelli_c{i}.addGobject('point', sprintf('cell centroid t%d', t+t_min-1), v);
                            else
                                for iii=1:length(index)
                                    v=[cord_new(index(iii)).Centroid(2)+rect(1,1)-1,  cord_new(index(iii)).Centroid(1)+rect(1,2)-1, z+z_min-1, t+t_min-1];
                                    pcelli_c{i}.addGobject('point', sprintf('cell centroid t%d', t+t_min-1), v);
                                end
                            end
                        end
                    end
                end
            end
        end
    end
end

summary = outputs.addTag('summary');
summary.addTag(sprintf('Number of cells being tracked'),noCells);
session.update('Saving results.');
session.finish();

end