function [X] = my_corner(I,disp,time,samp,RAD,PHI)


F = [];
flag = 0;
delta = clock;
D = diffmethod(I,1);    % get the information for the structure tensor
D = structureTensor(D,fspecial('gaussian',[12 12],2));   % make the structure tensor
D = cornerstrength(D,fspecial('average',[1 1])); % measure the tensor
[r,c] = nonmaxsuppts(D(:,:,6), 20, 10);  % find the peaks of the measure %% was 20 , 10 for takeshi
X = [r c];              % stack the location information

% if there is not any corner points then default to center point
if size(X,1) == 0
    X = size(I)/2;
    r = X(1);
    c = X(2);
    flag = 1;
end



% is sample is turned on then sample
if samp
    % if there are corners to sample at then perform sample
    if ~flag
        % make the sample grid
        [R T] = ndgrid(linspace(0,RAD,RAD),linspace(-pi,pi,PHI));
        X1 = R(:).*cos(T(:));
        X2 = R(:).*sin(T(:));   
        % for each point
        for i = 1:size(r,1)
            % sample the image and normalize
            temp = interp2(I,X1+c(i),X2+r(i));
            %temp = interp2(I,X1+c(i),X2+r(i));
            temp(isnan(temp(:))) = 0;
            temp = temp - mean(temp(:));
            % sample the corner strength
            CSt = interp2(D(:,:,6),c(i),r(i));
            %CSt = interp2(D(:,:,6),c(i),r(i));
            %CSt(isnan(CSt(:))) = 0;
            % binarize and PCA fit
            level = graythresh(temp/255);
            B = ~im2bw(temp/255,level);
            if sum(B(:)) == 0
                B(RADIUS+1,RADIUS+1) = 1;
                B(RADIUS+2,RADIUS+2) = 1;
            end
            fidx = find(B);    
            [SIM U BV L C ERR] = PCA_FIT([X1(fidx) X2(fidx)],2);
            
            if BV(1,1) < 0
                BV(:,1) = -BV(:,1);            
            end
            BV(:,2) = [-BV(2,1);BV(1,1)];
            
            
            % store, angle and the corner strength
            Z(i) = atan2(BV(2,1),BV(1,1));
            CS(i) = CSt;
            EIG(i,:) = [reshape(BV,[1 prod(size(BV))]) diag(L)'];
            F = [F ;temp'];            
        end
        % display
        if disp
            imshow(I,[])
            hold on
            %quiver(c,r,EIG(:,1),EIG(:,2),1,'r')            
            %quiver(c,r,EIG(:,3),EIG(:,4),1,'b')
            scatter(c,r,'r')
            hold off  
            drawnow
        end
    else
        Z = 0;
        EIG = zeros(1,6);
        CS = 0;
        F = zeros(1,RAD*PHI);
    end
    % stack the information
    % SZ = [2 1 6 1 N];
    X = [X Z' EIG CS' F];
end
if time
    etime(clock,delta)
end

%{
I = double(imread('Y:\takeshi\Maize\IBM lines\Gravitropism\IBM5s4\400000.tif'));
X = my_corner(I,1,1,1,20,100);
%}
