function [image_resource ErrorMsg] = MicrotubuleSegmentation(client_server, image_url, gauss_length, sigma_size, user, password)    
%--------------------------------------------------------------------------
%[image_resource ErrorMsg] = MicrotubuleSegmentation('http://bodzio.ece.ucsb.edu:8080', 'http://bodzio.ece.ucsb.edu:8080/ds/images/452', '', '', 'admin', 'admin')

ErrorMsg = '';
%addpath('./lib/');
irtdir = which('MicrotubuleSegmentation.m');
[irtdir dummy] = fileparts(irtdir);
clear dummy;
path([irtdir '/lib'], path)
disp(['Adding to java path ' [irtdir '/lib']]);
javaaddpath([irtdir '/lib']);
%%
javaaddpath('../lib/bisque.jar');
import bisque.*
%--------------------------------------------------------------------------
    disp('Importing ...');
    t=[];
    image_resource=[];
    try
        BQ = BQMatlab;
		BQ.initServers(client_server,client_server);
		BQ.login(user, password);
		
		image = BQ.loadImage(image_url);
        %urlImage = BQGetImage.getImageURL(image_url);
        x = str2double(image.x);
        y = str2double(image.y);
        z = str2double(image.z);		
        t = str2double(image.t);
        ch = str2double(image.ch);
        image.getInfo();
        d = str2double(image.d);
        %------------------------------------------------------------------
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
            im_in = uint16(BQ.loadImageData(image)); 
            if(isempty(im_in)); error(char(BQError.getLastError())); end
        else
            im_in = uint8(BQ.loadImageData(image));
            if(isempty(im_in)); error(char(BQError.getLastError())); end
        end
        disp('Formating ...');

        if ch==3 
            im_in=uint8(im_in(:,:,1));
        else
            im_in=uint8(im_in);
        end
        size_im = size(im_in);
     %------------------------------------------------------------------
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
                %out_im=mt_segmentation(in_im,if_filter,length_se,sigma_se,nr_dir_se,se_d,se_l,nr_dir_se2)
                im_seg=mt_segmentation(im_in,0,gauss_length,sigma_size,12,2,25,12);
            end
        end
        %------------------------------------------------------------------
        disp('Posting ...');
        %im_seg=uint8(im_in); 
        im_seg = uint8(im_seg)*255;
		new_image = BQ.initImage(size_im(1,1), size_im(1,2), 1, size_im(1,3), 1, 8, 'uint8', 1);
    	imageURL = BQ.saveImage(new_image, uint8(im_seg));
        if(isempty(imageURL)); error(char(BQError.getLastError())); end
    	new_tag = BQ.addTag(image, 'mask', char(imageURL));
    	response = BQ.saveTag(image, new_tag);
        disp('End :)');
    %----------------------------------------------------------------------
    if(~strcmp(char(BQError.getLastError()),'')); error(char(BQError.getLastError())); end    
    catch
        err = lasterror;
        ErrorMsg = err. message;
        return;
    end

end
