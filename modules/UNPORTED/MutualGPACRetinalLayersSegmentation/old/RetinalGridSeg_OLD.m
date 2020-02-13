%function image_resource = RetinalGridSeg(url, ImageID)    
function image_resource = RetinalGridSeg(client_server, image_url, user, password)
%--------------------------------------------------------------------------
%--------------------------------------------------------------------------
image_resource=[];
init();
disp('Importing ...');
im_in = imread('data (10).TIF');
load dat_gt_N_im10.mat;
try
    %[im_data ErrorCode ErrorMsg] = getImageData(url, ImageID);
    %im_in2 = readImage(url, im_data, 'jpeg');
    BQAuthorization.setAuthorization(user, password);
    im_in2 = uint8(BQGetImage.getImageData(image_url));            
    %----------------------------------------------------------------------
    disp('Segmentation ...')
    whole_prof = f_GetWholeTraining(im_in,pts_orig,r,c);
    boundary = f_GetBoundary_WithLoop(im_in2,whole_prof,r,c);
    size_s = size(im_in2);
    im_out = zeros(size_s(1,1),size_s(1,2));
    b_s = size(boundary);
    for i=1:b_s(1,2) 
        b_array = round(boundary{i});
        b_a_s = size(b_array);
        for j=1:b_a_s(1,1)-1
            im_out = func_Drawline(im_out, b_array(j,1), b_array(j,2), b_array(j+1,1), b_array(j+1,2), 255);
            %im_out(b_array(j,1),b_array(j,2)) = 1;
        end
    end
    se = strel('disk', 1);
    im_out = uint8(imdilate(im_out,se));
    %im_out=zeros(size(im_in2));
    %----------------------------------------------------------------------
    disp('Posting ...');
    %image_post = postImage(url, '/bisquik/upload_handler_mex', im_out, 'jpeg');
    %image_resource = findImageAttribute(image_post, 'uri');
    %maskTag = addTag('mask', image_resource);
    %postTag(url, ImageID, maskTag);
    size_im = size(im_out);
    BQAuthorization.setAuthorization(user, password);
    imageURL = BQPostImage.postImageData(client_server, uint8(im_out), 'uint8', size_im(1,1), size_im(1,2), 1, 1, 1);
    maskTag = BQTag.addTag('mask', char(imageURL), 'char');
    BQPostTag.postTag(image_url, maskTag);
    disp('End :)');
catch
    lasterror
    return;
end
%--------------------------------------------------------------------------
end

