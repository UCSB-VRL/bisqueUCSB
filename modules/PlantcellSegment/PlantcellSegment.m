function segmentedImage = PlantcellSegment(mex_url, access_token, image_url)

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

if length(d)==2
    d(3)=1;
    d(4)=1;
elseif length(d)==3
    d(4)=1;
end

for i=1:d(3)%Z direction
    for j=1:d(4)% T direction
        contours{i}{j}= bwboundaries(segmentedImage(:,:,i,j),'noholes');
        cord{i}{j}=regionprops(bwlabeln(segmentedImage(:,:,i,j)),'pixellist','PixelIdxList', 'Image','FilledImage','centroid');
    end
end

centroid = sObject.addGobject('Object', 'Centroids');
boundary = sObject.addGobject('Object', 'Boundaries');

for i=1:d(3) 
    for j=1:d(4)
        cord_new=cord{i}{j};
        centroid_zt{i}{j} = centroid.addGobject('Centroids', sprintf('Slice %d, Time %d', i+z_min-1,j+t_min-1));
        for ii=1:size(cord_new,1)
            v=[cord_new(ii).Centroid(2)+rect(1,1)-1,  cord_new(ii).Centroid(1)+rect(1,2)-1, i+z_min-1, j+t_min-1];
            centroid_zt{i}{j}.addGobject('point', sprintf('cell centroid %d', ii), v);
        end 
    end  
end

for i=1:d(3)
    for j=1:d(4)
        contours_new=contours{i}{j};
        boundary_zt{i}{j} = boundary.addGobject('Boundaries', sprintf('Slice %d, Time %d', i+z_min-1,j+t_min-1));
        for ii = 1 : size(contours_new, 1) %the ii-th contour
            contours_4=ContourSample(contours_new{ii},20);
            contours_4=contours_4+[rect(1,1)*ones(length(contours_4),1)  rect(1,2)*ones(length(contours_4),1)];
            contours_4d=[contours_4 (i+z_min-1)*ones(length(contours_4),1) (j+t_min-1)*ones(length(contours_4),1)];
            boundary_zt{i}{j}.addGobject('polygon', sprintf('Boundary %d', ii), contours_4d); %
        end
    end
end

summary = outputs.addTag('summary');

for i=1:d(3) 
    for j=1:d(4)
        cord_new=cord{i}{j};
        number=length(cord_new);
        summary.addTag(sprintf('Number of Segmented cells at Slice %d, Time %d', i+z_min-1,j+t_min-1),number);
    end  
end
% [ind1,ind2]=find(c{1}>0);
% 
% summary.addTag('matched cells 2',ind2');
session.update('Saving results.');
session.finish();

end