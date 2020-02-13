function [image_resource ErrorMsg] = SplinesRetinalLayersSegmentation(client_server, image_url,lambda, tps_iterations, user, password) %
%[image_resource ErrorMsg] = SplinesRetinalLayersSegmentation('http://bodzio.ece.ucsb.edu:8080', 'http://bodzio.ece.ucsb.edu:8080/ds/images/17074','admin', 'admin')
ErrorMsg = '';

addpath('./Retina_code/');
javaaddpath('../../lib/bisque.jar');
import bisque.*

global userErrorMsg;
image_resource = [];

try
%     if (strcmp(Retlayer,''))
%         Retlayer = 'ONL';
%     end
       
    BQ = BQMatlab;
    BQ.initServers(client_server,client_server);
    BQ.login(user, password);
    
    if (strcmp(lambda,''))
        lambda = 200;
    else
        lambda = str2num(lambda);
    end
    if (strcmp(tps_iterations,''))
        tps_iterations = 20;
    else
        tps_iterations = str2num(tps_iterations);
    end

%% Input image   
    image = BQ.loadImage(image_url);
    im_target = uint8(BQ.loadImageData(image)); 

    if(isempty(im_target)); error(char(BQError.getLastError())); end
    im_resized_target = imresize(im_target,[200 300],'nearest');
    
    temp = char(BQ.findTag(image, 'dataset_label'));
    if(isempty(temp) || ~strcmp(temp,'GPAC'))
        userErrorMsg = 'Selected Image has no valid tag information. Required tag- dataset_label:GPAC. Unable to perform Segmentation';
        error(userErrorMsg);
    end

    
%% Training phase
    % ??? some logic to be devised for setting the training flag
    % TODO : the training data to be stored on blob server
    training_flag=1;
    if(training_flag)

        im1_reference = char(BQ.findTag(image, 'reference_image')); 
        if(isempty(im1_reference)); error(char(BQError.getLastError())); end

        image = BQ.loadImage(im1_reference);
        im_training_full = uint8(BQ.loadImageData(image)); 
        if(isempty(im_training_full)); error(char(BQError.getLastError())); end

        image = BQ.loadImage(image_url);
        im2_reference = char(BQ.findTag(image, 'reference_mask'));
        if(isempty(im2_reference)); error(char(BQError.getLastError())); end

        image = BQ.loadImage(im2_reference);
        gt_full = uint8(BQ.loadImageData(image)); 
        if(isempty(gt_full)); error(char(BQError.getLastError())); end


        im_training = imresize(im_training_full,[200 300],'nearest');
        gt = imresize(gt_full,[200 300],'nearest');

        im = im2double(im_training);
        im_r = im(:,:,1);
        im_g = im(:,:,2);
        im_b = im(:,:,3);

        [n m l]=size(im);

        %Let's merge IS and OS
        gt((gt==9))=8;

        I = find(gt==1);
        rand_index = ceil(rand(10000,1)*length(I));
        [mixture, optmixture] = GaussianMixture([im_r(I(rand_index)),im_b(I(rand_index)),im_g(I(rand_index))], 15 , 0 , 0);
        optmixtureTotal{1} = optmixture;


        I = find(gt==11);
        rand_index = ceil(rand(10000,1)*length(I));
        [mixture, optmixture] = GaussianMixture([im_r(I(rand_index)),im_b(I(rand_index)),im_g(I(rand_index))], 15 , 0 , 0);
        optmixtureTotal{2} = optmixture;

        I = find(gt==7);
        rand_index = ceil(rand(10000,1)*length(I));
        [mixture, optmixture] = GaussianMixture([im_r(I(rand_index)),im_b(I(rand_index)),im_g(I(rand_index))], 15 , 0 , 0);
        optmixtureTotal{3} = optmixture;


        I = find(gt==8);
        rand_index = ceil(rand(10000,1)*length(I));
        [mixture, optmixture] = GaussianMixture([im_r(I(rand_index)),im_b(I(rand_index)),im_g(I(rand_index))], 15 , 0 , 0);
        optmixtureTotal{4} = optmixture;

    %     I = find(label==9);
    %     rand_index = ceil(rand(10000,1)*length(I));
    %     [mixture, optmixture] = GaussianMixture([im_r(I(rand_index)),im_b(I(rand_index)),im_g(I(rand_index))], 15 , 0 , 0);
    %     optmixtureTotal{5} = optmixture;

        %*****************************************
        % save('Trained_model.mat');
    else
        eval(['load ','Trained_model.mat']);
    end

    % close all;
    %
    % [x,y]=meshgrid(0:0.01:1);
    % figure; mesh(x,y,eval_2d_gmm(optmixtureTotal{1},x,y));xlabel('red');ylabel('blue');
    % figure; mesh(x,y,eval_2d_gmm(optmixtureTotal{2},x,y));xlabel('red');ylabel('blue');
    % figure; mesh(x,y,eval_2d_gmm(optmixtureTotal{3},x,y));xlabel('red');ylabel('blue');
    % figure; mesh(x,y,eval_2d_gmm(optmixtureTotal{4},x,y));xlabel('red');ylabel('blue');
    % figure; mesh(x,y,eval_2d_gmm(optmixtureTotal{5},x,y));xlabel('red');ylabel('blue');
    %Finished Training
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %image_name = '1DP41_equalize';
    %im_backup = im2uint8(imread([image_path,'/',image_name,'.TIF']));
    %im = im2double(imread([image_path,'/',image_name,'.TIF']));

    %im_backup = im2uint8(im_target);

%% Use the GMM of the training image to evaluate the boundaries

    % equalize channels
    for k = 1:3
        im1(:,:,k) = histeq(im_resized_target(:,:,k));
    end

    im = im2double(im1);

    im_r = im(:,:,1);
    im_g = im(:,:,2);
    im_b = im(:,:,3);
    [n m l]=size(im);

    %Evaluates the class probabilities
    feat = [im_r(:),im_b(:),im_g(:)];
    nlls = zeros(size(feat,1),length(optmixtureTotal));
    for kk = 1:length(optmixtureTotal)
        layer = optmixtureTotal{kk};
        for nn = 1:length(layer.cluster)
            cluster = layer.cluster(nn);
            mu = layer.cluster(nn).mu;
            R = layer.cluster(nn).R;
            dim = length(mu);
            pb  = layer.cluster(nn).pb;
            temp = feat-ones(size(feat,1),1)*mu.';
            temp2 = temp*inv(R);
            nll = sum(temp2.'.*temp.').';
            nlls(:,kk) = nlls(:,kk) + pb*1/sqrt((2*pi)^dim*det(R))*exp(-0.5*nll);
        end
    end

    for kk = 1:length(optmixtureTotal)
        Prob{kk}=reshape(nlls(:,kk),[size(im, 1), size(im, 2)]);
    end
    %Creates two different probability regions for the two background layers
    %(left and right)
    Prob{length(optmixtureTotal)+1}=Prob{1};
    Mask1=[ones(size(im, 1),floor(size(im, 2)/2)) zeros(size(im, 1),ceil(size(im, 2)/2))];
    Prob{1}=Prob{1}.*Mask1;
    Prob{length(optmixtureTotal)+1}=Prob{length(optmixtureTotal)+1}.*(1-Mask1);

    Norm_factor=zeros(size(Prob{1}));
    for kk = 1:length(optmixtureTotal)+1
        Norm_factor=Norm_factor+Prob{kk};
    end

    numel(find(Norm_factor==0))

    for kk = 1:length(optmixtureTotal)+1
        Prob{kk}=Prob{kk}./Norm_factor;
    end

    %%%%%%%%%%%%%%%%%%%%%%%%

    for kk = 1:length(optmixtureTotal)+1
        nlls2(:,kk)=reshape(Prob{kk},[size(im, 1)*size(im, 2) ,1]);
    end

    %This is the direct classification (i.e. every pixel is assigned to the
    %most likely class)
    [max_vals,max_inds] = max(nlls2,[],2);
    direct_class = reshape(max_inds,[size(im, 1), size(im, 2)]);

    % return;

    direct_class2=medfilt2(direct_class,[10 10]);

%% Estimate the boundaries based on the control points

    %Here we create the initial masks and signed distance functions
    S=regionprops(direct_class,'Centroid');
    InitMask=zeros(size(direct_class2));

    for kk = 1:length(optmixtureTotal)+1
        n_class_el(kk)=numel(find(direct_class==kk));
    end

    prev_cent=1;
    for kk = 1:length(optmixtureTotal)
        cent_ave=round((n_class_el(kk)*S(kk+1,1).Centroid+n_class_el(kk+1)*S(kk,1).Centroid)/(n_class_el(kk)+n_class_el(kk+1)));
        InitMask(:,prev_cent:cent_ave)=kk;
        prev_cent=cent_ave;
    end
    InitMask(:,cent_ave:end)=length(optmixtureTotal)+1;

    for kk = 1:length(optmixtureTotal)+1
        temp_mask=zeros(size(direct_class2));
        temp_mask(find(InitMask==kk))=1;
        edg=seg2bmap(temp_mask);
        T=Fast_Marching_OP(ones(size(direct_class2)),double(edg),zeros(size(direct_class2)));
        temp_phi=T; temp_phi(find(temp_mask==0))=-temp_phi(find(temp_mask==0));
        phi{kk}=temp_phi;

    end
    %Part related to the TPS
    min_dist=30;
    H=eye(3);
    %min_dist=18; easy case 17 tough case
    [ContrPoint ContrPointsInfo NCONPTS]=find_contr_pts2(im,min_dist);
    CtrPts=ContrPointsInfo(:,3:4)-1;
    CtrPts=[CtrPts ones(NCONPTS,1)]';

    TransCtrPts=inv(H)*CtrPts;
    TransCtrPts(1,:)=TransCtrPts(1,:)./TransCtrPts(3,:);
    TransCtrPts(2,:)=TransCtrPts(2,:)./TransCtrPts(3,:);
    TransCtrPts(3,:)=TransCtrPts(3,:)./TransCtrPts(3,:);

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %Create matrix A
    A=zeros(NCONPTS,NCONPTS);
    for i=1:1:NCONPTS
        for j=1:1:NCONPTS
            r=(TransCtrPts(1,i)-TransCtrPts(1,j))^2+(TransCtrPts(2,i)-TransCtrPts(2,j))^2;
            if(r~=0)
                A(i,j)=r*log(r);
            else
                A(i,j)=0;
            end
        end
    end

%   lambda is now a user controlled parameter
    %lambda=250000;
    %lambda=50000;
    %lambda=5000;
    A1=A+lambda*eye(NCONPTS,NCONPTS);
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %Create matrix P
    P=zeros(NCONPTS,3);
    P(:,1)=TransCtrPts(3,:)';
    P(:,2)=TransCtrPts(1,:)';
    P(:,3)=TransCtrPts(2,:)';
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %Create matrix P
    K=[A1 P; P' zeros(3,3)];
    K_inv=K\eye(size(K));
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %Create matrix B and Q
    B=zeros(n*m,NCONPTS);
    Q=zeros(n*m,3);
    for j=1:1:m
        for i=1:1:n
            for k=1:1:NCONPTS
                r=((i-1)-TransCtrPts(1,k))^2+((j-1)-TransCtrPts(2,k))^2;
                if(r~=0)
                    B(i+(j-1)*n,k)=r*log(r);
                else
                    B(i+(j-1)*n,k)=0;
                end
            end
            Q(i+(j-1)*n,:)=[1 i-1 j-1];
        end
    end

    M=[B Q];
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    X_CON=(CtrPts(1:2,:))';
    X_CON=[X_CON;zeros(3,2)];

    MKinv=M*K_inv;
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    mask=ones(n,m);

%% Spline warping

    for i=1:1:tps_iterations
            disp(i);
        [X_CON]=Mutual_CV_Multi_TPS(phi,Prob,2000,double(mask),MKinv, X_CON);
         clear outt;
        [New_mask] = CanvasWarpTPS(InitMask, MKinv, X_CON, [n; m]);

        segmentation=round(New_mask);
        edges=seg2bmap(segmentation);
        temp=im(:,:,1); temp(find(edges==1))=1; b(:,:,1)=temp;
        temp=im(:,:,2); temp(find(edges==1))=1; b(:,:,2)=temp;
        temp=im(:,:,3); temp(find(edges==1))=1; b(:,:,3)=temp;

    end

%% Rescale the mask and save the mask

        rescaled_mask = imresize(New_mask,[size(im_target,1) size(im_target,2)],'nearest');
        if(isempty(rescaled_mask)); error(char(BQError.getLastError())); end

        new_image = BQ.initImage(size(im_target,1), size(im_target,2), 1, 1, 1, 8, 'uint8', 1);
        segmented_imageURL = BQ.saveImage(new_image, uint8(rescaled_mask));    

        %if a tag already exists, delete the old mask and the tag
        BQ_image_obj = BQ.loadImage(image_url);
        saved_img_url = char(BQ.findTag(BQ_image_obj,'Splines_Seg_Mask'));
        if(~isempty(saved_img_url))
            BQ.deleteImage(saved_img_url);
            BQ.deleteTag(BQ_image_obj,'Splines_Seg_Mask');
        end
       
        gt_tag = BQ.addTag(BQ_image_obj,'Splines_Seg_Mask', char(segmented_imageURL));
        BQ.saveTag(BQ_image_obj, gt_tag);  

%% Save the mask as GObjects
        rescaled_edges = imresize(edges,[size(im_target,1) size(im_target,2)],'nearest');
        [ErrorMsg segm_pts num_layers] = edgemap2seg(rescaled_edges,15);
        retina_save_segm_out(image_url,segm_pts,num_layers);

catch
    if (~strcmp(userErrorMsg,''))
        ErrorMsg = userErrorMsg;
    else
        err = lasterror;
        ErrorMsg = err. message;
    end
    return;
end
end

%% Save the segmentation results as GObject in the input image
function retina_save_segm_out(image_url,segm_pts, num_layers)

    import bisque.*
    BQ = BQMatlab;
          % for now, assume only one GT data exists
    % look here for adding profile data

    %Delete existing Segmentation_Output results
    in_image_deep = BQ.loadImage([image_url '?view=deep']);
    image_gobj = in_image_deep.gobjects;
    for i = 0:size(image_gobj)-1
        if(strcmp(image_gobj.get(i).name,'Splines_Output_SEG_data'))
            BQ.deleteGObject(image_gobj.get(i));
        end
    end
    segm_layers={'boundary_bg/GCL';'boundary_GCL/INL';'boundary_INL/ONL';'boundary_ONL/IS';'boundary_IS/bg'};
    %add GObjects to it
    polyline_set = BQ.createGObject('polyline_set','Splines_Output_SEG_data');

    %create a GObject for every layer
    for cur_layer = 1:num_layers
        %every layer will have a polyline
        polyline = BQ.createGObject('polyline',segm_layers{cur_layer});

       %now add the vertices to the polyline from the pts set
        cur_layer_temp = segm_pts{cur_layer};
        for i = 1:length(cur_layer_temp)
            vert = [cur_layer_temp(i,1),cur_layer_temp(i,2)];
            BQ.addVertices(polyline,vert);
        end

         %add the current layer to gt_data
        BQ.addGObject(polyline_set,polyline);
    end

    %finally add the gt_data to the image
    BQ_image_obj = BQ.loadImage(image_url);
    polyline_GObjectURL = char(BQ.saveGObjectURL(BQ_image_obj,polyline_set));   

    %add tags to the segmentation output
    BQ.deleteTag(BQ_image_obj,'Splines_Seg_GObj');
    tag = BQ.addTag(BQ_image_obj,'Splines_Seg_GObj',char(polyline_GObjectURL));
    if(isempty(tag)); error(char(BQError.getLastError())); end   
    res = BQ.saveTag(BQ_image_obj, tag);
    if(isempty(res)); error(char(BQError.getLastError())); end         

end
    
%% Convert the edge map to segmentation points
function [ErrorMsg segm_pts layer_num] = edgemap2seg(image,interval)

    ErrorMsg = '';
    [height, width] = size(image);
    layer_num = 1;
    rows = [1:interval:height height];
    try
         %do for all the intervals
            for i = rows
                layer_num = 1;
                cur_row = image(i,:);
                boundary = find(cur_row~=0);
                index = ceil(i/interval);

                segm_pts{layer_num}(index,1) = boundary(1);
                segm_pts{layer_num}(index,2) = i;
                for j = 2:length(boundary)
                    if(abs(boundary(j) - boundary(j-1))~=1)                       
                        layer_num = layer_num +1;
                        segm_pts{layer_num}(index,1) = boundary(j);
                        segm_pts{layer_num}(index,2) = i;
                    end                                        
                end
            end
    catch
         err = lasterror;
        ErrorMsg = err. message;
        return;
    end
end
