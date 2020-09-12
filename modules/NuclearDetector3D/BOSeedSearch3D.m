%% BOSeedSearch3D - finding seeds
%    npo = BOSeedSearch3D(im, ns, t)
%
%   INPUT:
%       im      - LoG of nuclei channel
%       ns      - nuclear size
%       t       - a rannge of lowest intensity bounds
%
%   OUTPUT:
%       npo     - a cell with detected nuclei positions for each threshold
%                 an individual cell is a matrix of form:
%                   npo{t}(:,1) -> Y coordinate (starting at 1)
%                   npo{t}(:,2) -> X coordinate (starting at 1)
%                   npo{t}(:,3) -> Z coordinate (starting at 1)
%                   npo{t}(:,4) -> point IDs
%
%   AUTHOR:
%       Boguslaw Obara, http://boguslawobara.net/
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       0.1 - 30/06/2009 First implementation
%       0.2 - 04/06/2010 Revision
%       0.3 - 24/09/2010 Speed up
%       0.4 - 15/10/2010 New local maxima
%       0.5 - 2011-06-04 by Dmitry: support for a threshold range
%       0.6 - 2013-09-20 by Dmitry: speed-up by 25X by approximating 3D dilation 
%             with 2 2D dilations
%       0.7 - 2013-09-21 by Dmitry: speed-up by 10X times with GPU
%%

function npo = BOSeedSearch3D(im, ns, t)
    %% cube is 10 times faster - Matlab converts it into 1D line elements
    %se = ones(round(2.0*ns+1.0));

    ns = round(ns);       
    fprintf('Dilation\n');  
    
    %% full 3D dilation - N1 slowest thing in the code now
    %se = se_ellipse(ns);
    %se = se_diamond(ns); 
    %tic;
    %immax = imdilate(im, se, 'notpacked', 'same');
    %all = find(im==immax);
    %clearvars immax;  
    %toc
    
    %% approximated 3D dilation - 25X faster
    se_xy = se_ellipse_xy(ns); 
    se_yz = se_ellipse_yz(ns); 
    
    tic;      
%     try
%         % approximated 3D dilation on a GPU - additional 10X but uses uint8
%         % produces more points and takes much longer in filtering
%         imu = norm_uint8(im);
%         immax = dilate_gpu(imu, se_xy, se_yz);
%         idx = find(imu==immax);
%         clearvars imu immax;
%     catch err
        immax = dilate_fast(im, se_xy, se_yz);
        idx = find(im==immax);
        clearvars immax;        
%     end    
    toc    
    
    %% find candidates
    fprintf('Finding candidates\n');  
    tic;
    
    %% extract candidate locations for given thresholds
    npo = cell(length(t),1);
    for i = 1:length(t),
        idx(im(idx)<t(i)) = [];

        [xc,yc,zc] = ind2sub(size(im),idx);
        np = [xc yc zc];  

        [~,idxs] = sort(im(idx),'descend');
        np = np(idxs,:);    
        np(:,4) = (1:size(np,1))';
        npo{i} = np;
    end
    toc
end

function im = dilate_fast(im, se_xy, se_yz)
    im = imdilate(im, se_xy, 'same');
    im = shiftdim(im,2);
    im = imdilate(im, se_yz, 'same');
    im = shiftdim(im,1);
end

function im = dilate_gpu(im, se_xy, se_yz)
    imgpu = gpuArray(im);
    imgpu = imdilate(imgpu, se_xy, 'same');
    imgpu = shiftdim(imgpu,2);
    imgpu = imdilate(imgpu, se_yz, 'same');
    imgpu = shiftdim(imgpu,1);        
    im = gather(imgpu);
end

function im = norm_uint8(im)
    imin = min(im(:));
    irange = max(im(:))-imin;        
    im = uint8(single(im-imin)./single(irange)*255.0);
end

function se = se_ellipse(ns)
    [xg,yg,zg] = meshgrid(-ns(1):ns(1),-ns(2):ns(2),-ns(3):ns(3));
    se = ( (xg/ns(1)).^2 + (yg/ns(2)).^2 + (zg/ns(3)).^2 ) <= 1;
    se = strel('arbitrary', se);
end

function se = se_ellipse_xy(ns)
    ns(1:2) = ns(1:2) ./ 2;
    [xg,yg] = meshgrid(-ns(1):ns(1),-ns(2):ns(2));
    se = ( (xg/ns(1)).^2 + (yg/ns(2)).^2 ) <= 1;
    %se = strel('arbitrary', se);
end

function se = se_ellipse_yz(ns)
    ns(1:2) = ns(1:2) ./ 2;
    [yg,zg] = meshgrid(-ns(2):ns(2),-ns(3):ns(3));
    se = ( (yg/ns(2)).^2 + (zg/ns(3)).^2 ) <= 1;
    %se = strel('arbitrary', se);
end

function se = se_diamond(ns)
    [rr,cc,ll] = meshgrid(-ns(1):ns(1),-ns(2):ns(2),-ns(3):ns(3));
    g = abs(rr) + abs(cc) + abs(ll);
    se = g<=max(ns);
    
    stop = size(se,3)+1;
    step = (max(ns) - min(ns)) / ns(3);
    lim = min(ns);
    for i=1:ns(3),
        t = g<=lim;
        se(:,:,i) = t(:,:,i);
        se(:,:,stop-i) = t(:,:,i);
        lim = lim + step;        
    end
    se = strel('arbitrary', se);
end

