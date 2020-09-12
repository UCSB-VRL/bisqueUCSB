function [image_resource ErrorMsg] = Kmeans(client_server, image_url, color_space, number_of_clusters, user, password)

%[image_resource ErrorMsg] = Kmeans('http://bodzio.ece.ucsb.edu:8080', 'http://bodzio.ece.ucsb.edu:8080/ds/images/449', 'RGB', '2', 'admin', 'admin')

%usage: [image_resource ErrorMsg] =
%Watershed('http://water.ece.ucsb.edu:8080','http://water.ece.ucsb.edu:8080/ds/images/3543', color_space, number_of_clusters, user, password);
%----------------------------------------------------------
% im : image to cluster with k-means
% color-space : 'RGB' if you want to cluster in RGB color-space
%               'Lab' if you want to cluster in L*a*b* color-space
% number_of_clusters : total of clusters you want

% Output
%-------------------------------------------------------------
% clusters_index: image where the clusters are labeled by it's
%                 clusternumber
% clusters_centra: image where the clusters are labeled by it's centra
%                  color
% cluster: number_of_clusters images with in each image the pixels of the
%          original image of the corrensponding image
% Result(filter size,min_dist)_p_totalarea

addpath('../');

javaaddpath('../../lib/bisque.jar');
import bisque.*

ErrorMsg = '';
image_resource = [];
try
	BQ = BQMatlab;
    BQ.initServers(client_server,client_server);
    BQ.login(user, password);


    if (strcmp(color_space,''))
        color = 'RGB';
    else
        color = color_space; 
    end
    if (strcmp(number_of_clusters,''))
        error(char(BQError.getLastError()));
    else
        nColors = str2double(number_of_clusters); 
    end
   
%     original_im = image_url;
    image_o = BQ.loadImage(image_url);
    original_im = uint8(BQ.loadImageData(image_o)); 
    %original_im = uint8(BQImage.getImage(image_url));
    if(isempty(original_im)); error(char(BQError.getLastError())); end
 
    switch color
        case 'RGB'
            im = original_im;
            num = 3;
        case 'Lab'
            cform = makecform('srgb2lab');
            im = applycform(original_im, cform);
            num = 2;
    end
    
    colorsp = double(im(:, :, (4-num):3));
    nrows = size(colorsp, 1);
    ncols = size(colorsp, 2);
    colorsp = reshape(colorsp, nrows*ncols, num);
    
    [cluster_idx cluster_center] = kmeans(colorsp, nColors, 'distance', 'sqEuclidean', 'emptyaction', 'singleton');
    
    if num == 3
        graycenter = 0.2989 * cluster_center(:,1) + 0.5870 * cluster_center(:,2) + 0.1140 * cluster_center(:,3);
    elseif num ==2
        graycenter = 0.2989 * cluster_center(:,1) + 0.5870 * cluster_center(:,2);
    end
    
    cluster_center_ordered(:,1) = graycenter;
    cluster_center_ordered(:,2) = 1:nColors;
    cluster_center_ordered(:,3:(2+num)) = cluster_center;
    cluster_center_ordered = sortrows(cluster_center_ordered,1);
    
    tmp = cluster_idx;
    for i = 1:nColors
        tmp(cluster_idx == i) = find(cluster_center_ordered(:,2) == i);
    end
    cluster_idx = tmp;
    clear tmp
    
    cluster_center_ordered(:,1:2) = [];
    
    clusters_index = reshape(cluster_idx, nrows, ncols);
    
    cluster = cell(1,3);
    rgb_label = repmat(clusters_index,[1 1 3]);
    
    if num == 3
        clusters_centra = im;
    end
    
    tmp1 = im(:,:,1);
    tmp2 = im(:,:,2);
    tmp3 = im(:,:,3);
    
    for i = 1:nColors
        colorim = original_im;
        colorim(rgb_label ~= i) = 0;
        cluster{i} = colorim;
        clear colorim
        
        if num == 3
             tmp1(clusters_index == i) = cluster_center_ordered(i,1);
            tmp2(clusters_index == i) = cluster_center_ordered(i,2);
            tmp3(clusters_index == i) = cluster_center_ordered(i,3);
        end
    end
    
    if num == 3
        clusters_centra(:,:,1) = tmp1;
        clusters_centra(:,:,2) = tmp2;
        clusters_centra(:,:,3) = tmp3;
    end
    clear tmp1 tmp2 tmp3

    maxclus=max(max(clusters_index));
    minclus=min(min(clusters_index));
    clusters_index=(clusters_index-minclus)/(maxclus-minclus);
    
%     figure; imshow(clusters_index) 
%     figure; imshow(clusters_centra)
%     for i=1:nColors
%         figure; imshow(cluster{i})
%     end
     
     
    size_im = size(clusters_index);

    new_image = BQ.initImage(size_im(1,1), size_im(1,2), 1, 1, 1, 8, 'uint8', 1);
    imageURL = BQ.saveImage(new_image, uint8(clusters_index));    
    if(isempty(imageURL)); error(char(BQError.getLastError())); end
    %imageURL = BQImage.postImage(client_server, uint8(clusters_index), 'uint8', size_im(1,1), size_im(1,2), 1 , 1, 1,1);
    %if(isempty(imageURL)); error(char(BQError.getLastError())); end
    sprintf('%s', char(imageURL))
    
    
    tag = BQ.addTag(image_o, 'clusters_index', char(imageURL));
    if(isempty(tag)); error(char(BQError.getLastError())); end 
    response = BQ.saveTag(image_o, tag);        
    if(isempty(response)); error(char(BQError.getLastError())); end
    
    %tag = BQTag.addTag('clusters_index', char(imageURL), 'char');
    %response = BQTag.postTag(image_url, tag);
    
    img_tag = BQ.addTag(new_image, 'image', char(imageURL));
    if(isempty(tag)); error(char(BQError.getLastError())); end 
    response = BQ.saveTag(new_image, img_tag);        
    if(isempty(response)); error(char(BQError.getLastError())); end

    %img_tag = BQTag.addTag('image', char(image_url), 'char');
    %if(isempty(img_tag)); error(char(BQError.getLastError())); end
    %response = BQTag.postTag(char(imageURL), img_tag);
    %if(isempty(response)); error(char(BQError.getLastError())); end
    
    size_im2 = size(clusters_centra);
    new_image = BQ.initImage(size_im2(1,1), size_im2(1,2), 1, 1, size_im2(1,3), 8, 'uint8', 1);
    imageURL = BQ.saveImage(new_image, uint8(clusters_centra));    
    if(isempty(imageURL)); error(char(BQError.getLastError())); end
    
    
    %imageURL = BQImage.postImage(client_server, uint8(clusters_centra), 'uint8', size_im2(1,1), size_im2(1,2), size_im2(1,3), 1, 1,1);
    %if(isempty(imageURL)); error(char(BQError.getLastError())); end

    
    tag1 = BQ.addTag(new_image, 'clusters_centra', char(imageURL));
    if(isempty(tag1)); error(char(BQError.getLastError())); end 
    response = BQ.saveTag(new_image, tag1);        
    if(isempty(response)); error(char(BQError.getLastError())); end
    
    %tag = BQTag.addTag('clusters_centra', char(imageURL), 'char');
    %if(isempty(tag)); error(char(BQError.getLastError())); end 
    %response = BQTag.postTag(image_url, tag);
    %if(isempty(response)); error(char(BQError.getLastError())); end
   
    
    tag2 = BQ.addTag(new_image, 'image', char(image_url));
    if(isempty(tag2)); error(char(BQError.getLastError())); end 
    response = BQ.saveTag(new_image, tag2);        
    if(isempty(response)); error(char(BQError.getLastError())); end
    
    %img_tag = BQTag.addTag('image', char(image_url), 'char');
    %if(isempty(img_tag)); error(char(BQError.getLastError())); end
    %response = BQTag.postTag(char(imageURL), img_tag);
    %if(isempty(response)); error(char(BQError.getLastError())); end
    
    for i=1:nColors
        size_im3 = size(cluster{i}); 
        new_image = BQ.initImage(size_im3(1,1), size_im3(1,2), 1, 1, size_im3(1,3), 8, 'uint8', 1);
        imageURL = BQ.saveImage(new_image, uint8(cluster{i}));    
        if(isempty(imageURL)); error(char(BQError.getLastError())); end

        tag = BQ.addTag(image_o, ['cluster ',num2str(i)], char(imageURL));
        if(isempty(tag)); error(char(BQError.getLastError())); end 
        response = BQ.saveTag(image_o, tag);        
        if(isempty(response)); error(char(BQError.getLastError())); end
        img_tag = BQ.addTag(new_image, 'image', char(image_url));
        if(isempty(tag)); error(char(BQError.getLastError())); end 
        response = BQ.saveTag(new_image, img_tag);        
        if(isempty(response)); error(char(BQError.getLastError())); end
       
%         imageURL = BQImage.postImage(client_server, uint8(cluster{i}), 'uint8', size_im3(1,1), size_im3(1,2),size_im3(1,3), 1, 1, 1);
%         if(isempty(imageURL)); error(char(BQError.getLastError())); end
%         
%         tag =  BQTag.addTag(['cluster ',num2str(i)], char(imageURL), 'char');
%         if(isempty(tag)); error(char(BQError.getLastError())); end 
%         response = BQTag.postTag(image_url, tag);
%         if(isempty(response)); error(char(BQError.getLastError())); end
%         img_tag = BQTag.addTag('image', char(image_url), 'char');
%         if(isempty(img_tag)); error(char(BQError.getLastError())); end
%         response = BQTag.postTag(char(imageURL), img_tag);
%         if(isempty(response)); error(char(BQError.getLastError())); end
    end
    if(~strcmp(char(BQError.getLastError()),'')); error(char(BQError.getLastError())); end
catch
    err = lasterror;
    ErrorMsg = err. message;
    return;
end

end
