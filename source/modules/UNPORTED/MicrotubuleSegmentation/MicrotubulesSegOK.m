function image_resource = MicrotubulesSegOK(url, ImageID, gauss_length, sigma_size)    
%--------------------------------------------------------------------------
%path(path,'./lib')   
%path(path,'./lib_bisquik')
%javaclasspath
%--------------------------------------------------------------------------
disp('Importing ...');
t=[];
image_resource=[];
try
    BQAuthorization.setAuthorization('admin','admin');
    urlImage = BQGetImage.getImageURL([url ImageID]);
	arrayImageInfo = BQGetImage.getImageInfo(urlImage);
	x = str2double(BQGetImage.searchImageInfo(arrayImageInfo, 'height'));
	y = str2double(BQGetImage.searchImageInfo(arrayImageInfo, 'width'));
	z = str2double(BQGetImage.searchImageInfo(arrayImageInfo, 'zsize'));		
	t = str2double(BQGetImage.searchImageInfo(arrayImageInfo, 'tsize'));
	d = str2double(BQGetImage.searchImageInfo(arrayImageInfo, 'depth'));
catch
    lasterror
    return;
end
%--------------------------------------------------------------------------

try
        if strcmp(gauss_length,'gauss_length') 
            gauss_length=5;
        else
            gauss_length=str2double(gauss_length);
        end
        if strcmp(sigma_size,'sigma_size')
            sigma_size=2; 
        else
            sigma_size=str2double(sigma_size); 
        end
        
        if d==16
            im_in = uint16(BQGetImage.getImageData([url ImageID]));            
        else
            im_in = uint8(BQGetImage.getImageData([url ImageID]));            
        end
        disp('Formating ...');
        size_im = size(im_in);
        %{
        if length(size_im)==3 
            if size_im(1,3)==3
                im_in=uint8(im_in(:,:,1));
            elseif size_im(1,3)==1
                im_in=uint8(im_in);
            else
                return;
            end
        else
            im_in=uint8(im_in);
        end
        %}
        %--------------------------------------------------------------------------
        disp('Segmentation ...')
        resolution_im = 0;
        if length(size_im)==3
            %im_seg=logical(zeros(size_im)); 
            im_seg=uint8(zeros(size_im)); 
            for i=1:size_im(1,3)
                if resolution_im==0 
                    im_seg(:,:,i)=mt_segmentation(im_in(:,:,i),0,gauss_length,sigma_size,12,2,25,12);
                else
                    im_seg(:,:,i)=mt_segmentation(im_in(:,:,i),0,gauss_length,sigma_size,12,2,25,12);
                end
            end
        else
            if resolution_im==0 
                im_seg=mt_segmentation(im_in,0,gauss_length,sigma_size,12,2,25,12);
            else
                %resolution_im=;
                %if_filter=;
                %length_se=;
                %sigma_se=;,
                %nr_dir_se
                %se_d=;
                %se_l=;
                %nr_dir_se2=;
                %out_im=mt_segmentation(in_im,if_filter,length_se,sigma_se,nr_dir_se,se_d,se_l,nr_dir_se2)
                im_seg=mt_segmentation(im_in,0,gauss_length,sigma_size,12,2,25,12);
            end
        end
%--------------------------------------------------------------------------
        disp('Posting ...');
        %image_post = postImageSlice(url, '/bisquik/upload_handler_mex', im_seg, 'jpeg');
        response = BQPostImage.postImageData('http://bodzio.ece.ucsb.edu:8080', ...
                                    im_seg, 'uint8', size_im(1,1), size_im(1,2), 1, 1, 5);

        %image_post = postImage(url, '/bisquik/upload_handler_mex', im_seg, 'jpeg');
        %image_resource = findImageAttribute(image_post, 'uri');
        maskTag = addTag('mask', image_resource);
        postTag(url, ImageID, maskTag);
        disp('End :)');
%--------------------------------------------------------------------------
    catch
        lasterror
        return;
    end
end
