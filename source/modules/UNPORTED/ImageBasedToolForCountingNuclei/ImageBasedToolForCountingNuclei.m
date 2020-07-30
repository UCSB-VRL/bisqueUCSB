function [image_resource ErrorMsg] = ImageBasedToolForCountingNuclei(client_server, image_url, filter_size, min_distance, channelNum, invOption,mask_image, user, password)
%[image_resource ErrorMsg] = ImageBasedToolForCountingNuclei('http://bodzio.ece.ucsb.edu:8080', 'http://bodzio.ece.ucsb.edu:8080/ds/images/116', '', '', '', 'admin', 'admin')

% updated - 6/5/2009
% area calculation bug removed. Creating gobjects. Creating better tags
% sharath@cs.ucsb.edu

% Input
%-------------------------------------------------------------
% im = image to count cells
% side: filter size - choose the diameter (or slightly larger) of the blob (in pixels)
% min_dist : minimum distance between peaks
% option : 1 if the peak to detect is dark
%          0 if the peak to detect is bright (e.g. Topro stained image)
% map : mask of layer
% th : threshold for filter output
      %- suggested to choose -0.05 or 0

% Output
%-------------------------------------------------------------
% p: returns the number of peaks (cells) detected.
% image_resource: resultImaage 
% Result(filter size,min_dist)_p_totalarea

% Works only with gray-scale images. If RGB image is input, the image will
% be converted to gray image

%
% Protocol to talk to bisquik
javaaddpath('../../lib/bisque.jar');
import bisque.*

ErrorMsg = '';
image_resource = '';

%% Init
try

	BQ = BQMatlab;
    BQ.initServers(client_server,client_server);
    BQ.login(user, password);

    if (strcmp(filter_size,''))
        filterSize = 10.0;
    else
        filterSize = str2double(filter_size); 
    end
    if (strcmp(min_distance,''))
        minDist = 5.0;
    else
        minDist = str2double(min_distance); 
    end
 
%% Load Image 
    image = BQ.loadImage(image_url);
    channel_Nuclei = str2double(channelNum);
    im = BQ.loadImageDataCH(image, channel_Nuclei);
    if(isempty(im)); error(char(BQError.getLastError())); end
           
    if strcmp(mask_image,'ONL')
        mask_image = char(BQ.findTag(image, 'GroundTruth_ONL'));
        image_gt = BQ.loadImage(mask_image);
        gt = uint8(BQ.loadImageData(image_gt));
        if(isempty(gt)); error(char(BQError.getLastError())); end
        
        %if the mask is not of the same size, resize the mask
        [im_y im_x im_z] = size(im);
        [gt_y gt_x gt_z] = size(gt);
        if((gt_x ~= im_x) || (gt_y ~= im_y))
            gt = imresize(gt, [im_y im_x],'nearest');
        end
 
    else
         gt = uint8(255.*ones(size(im,1),size(im,2)));
    end
  
%% calculate area of the region and get info from the tags
    pixel_resolution_x = char(BQ.findTag(image, 'pixel_resolution_x'));
    pixel_resolution_y = char(BQ.findTag(image, 'pixel_resolution_y'));
    pixel_resolution_xy = char(BQ.findTag(image, 'pixel_resolution_xy'));
    
    if(isempty(pixel_resolution_x) || isempty(pixel_resolution_y) )
        if(~isempty(pixel_resolution_xy))
            pixel_resolution_x = str2double(pixel_resolution_xy);
            pixel_resolution_y = str2double(pixel_resolution_xy);
        else
            pixel_resolution_x = -1;
            pixel_resolution_y = -1;
        end 
    end
   
    map =zeros(size(im,1),size(im,2));
    % ONL == 7 in gt
    map(find(gt==255))= 1;
   
    %mag = 0.621481;
    %area_onl = calculateArea(gt, 255, mag); %area_onl = sum(nonzeros(logical(gt(:))));
    
    area_pixels = length(find(gt==255));
    
    if(pixel_resolution_x > 0)
        area_microns = area_pixels *pixel_resolution_x*pixel_resolution_y;
    else
        area_microns = -1;
    end
%% Channel,option 

%    if size(im,3) ==1
%		img = im;
%	else
%		img = rgb2gray(im);
%	end
	img =uint8(im);
    
    option = str2double(invOption);
	if option==0
		img = 255-img;
	end
	
	% apply the filter
    th =0;
	ac = lapofgau(img,filterSize);
	ac(find(ac<th))=th;
	ac = ac-th;
	
	scaling = 1;
	ac2=ac;
	%figure; imagesc(ac); axis image; axis off
	
%% find local maxima from filter output
	[i,j,val] = find_local_max_2D(ac2,[],floor(filterSize/4/scaling),inf,minDist,[],[1 1],map);
	
	p =0;
	ind=[];
	tmp = [i' j' ];
    s=size(im);
    result=uint8(zeros(s(1,1),s(1,2)));
    
    for k =1: length(i)
        p = p+1;
        result(tmp(k,1), tmp(k,2))= 255;
    end
	
	cellDensity_pix= (p/area_pixels);
    cellDensity_microns= (p/area_microns);
    
    size_im = size(result);
  
%% Output   
    % create the gobjects
    go = BQ.createGObject('NucleiDetector',datestr(now));
    for temp=1:length(i)
        point = BQ.createGObject('point',num2str(temp));
        vertex = [j(temp) i(temp)];
        BQ.addVertices(point,vertex);
        BQ.addGObject(go, point);
    end

    %save the tags
    image = BQ.loadImage([image_url '?view=full']);
    BQ.deleteGObjectFull(image);
    gobject_url = char(BQ.saveGObjectURL(image,go));
    
    nucleiTag = BQ.createTag(['NucleiDetection ' datestr(now,31)],'');
    BQ.saveTag(image, nucleiTag);
    
    nucleiCountTag = BQ.createTag('nuclei_count', num2str(length(i)));
    nucleiDensityPixTag = BQ.createTag('nuclei_density/pixel', num2str(cellDensity_pix)); 
    nucleiGObjectsTag = BQ.createTag('gobject_url', gobject_url);
    
    BQ.addTag(nucleiTag, nucleiCountTag);
    BQ.addTag(nucleiTag, nucleiDensityPixTag);
    BQ.addTag(nucleiTag, nucleiGObjectsTag);
    
    BQ.saveTagURL(nucleiTag, nucleiCountTag);
    BQ.saveTag(nucleiTag, nucleiGObjectsTag);
    BQ.saveTag(nucleiTag, nucleiDensityPixTag);
    
    if(cellDensity_microns > 0)
        nucleiDensityMicronsTag = BQ.createTag('nuclei_density/micron', num2str(cellDensity_microns)); 
        BQ.addTag(nucleiTag, nucleiDensityMicronsTag);
        BQ.saveTag(nucleiTag, nucleiDensityMicronsTag);
    end

    %save the mask image
    new_image = BQ.initImage(size_im(1,1), size_im(1,2), 1, 1, 1, 8, 'uint8', 1);
    imageURL = BQ.saveImage(new_image, uint8(result));    
    if(isempty(imageURL)); error(char(BQError.getLastError())); end
    
    nucleiMaskImageTag = BQ.addTag(nucleiTag, 'output_mask_image', char(imageURL));
    response = BQ.saveTag(nucleiTag, nucleiMaskImageTag);    
    if(isempty(response)); error(char(BQError.getLastError())); end
    
    if(~strcmp(char(BQError.getLastError()),'')); error(char(BQError.getLastError())); end
catch
    err = lasterror;
    ErrorMsg = err. message;
	return;
end

end
