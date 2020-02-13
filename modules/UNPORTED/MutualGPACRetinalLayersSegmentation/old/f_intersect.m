function pt_int = f_intersect(pt_a,pt_b);

% pt_int = f_intersect(pt_a1
% pt_a = 4 x 1
% pt_b = 4 x N where pt_bx(4,k) = [x1 y1 x2 y2]' coordinates

pt_a1 = pt_a(1:2);
pt_a2 = pt_a(3:4);
pt_b1 = pt_b(1:2,:);
pt_b2 = pt_b(3:4,:);

%------convert line into the form ax + by = c -------------

% line a
a1 = pt_a2(2)-pt_a1(2);
b1 = pt_a1(1)-pt_a2(1);
c1 = a1.*pt_a1(1)+b1.*pt_a1(2);

% line b
a2 = pt_b2(2,:)-pt_b1(2,:);
b2 = pt_b1(1,:)-pt_b2(1,:);
c2 = a2.*pt_b1(1,:)+b2.*pt_b1(2,:);

%------compute intersection point of lines a and b----------

% denominator
den = a1*b2 - a2*b1;

% numerators
numx = b2*c1 - b1*c2;
numy = a1*c2 - a2*c1;

% indices of zero denominator (parallel or incident lines)
z_den = den == 0;

% indices of zero numerators (may indicate incident lines)
z_numx = numx == 0;
z_numy = numy == 0;

% incident lines only
ind_in = z_den & z_numx & z_numy;

% parallel lines only
ind_para = z_den & ~ind_in;

% initialize intersection pt (leave as -1 for parallel lines)
pt_intx = -1*ones(1,size(pt_b1,2));
pt_inty = pt_intx;

% non parallel or incident
pt_intx(~z_den) = numx(~z_den)./den(~z_den);
pt_inty(~z_den) = numy(~z_den)./den(~z_den);

% incident (take midpt between closest endpts)

ind_in2 = find(ind_in);
if ~isempty(ind_in2),
    % find closest pt to pt_a1
    pt_a1_mat = repmat(pt_a1,1,length(ind_in2));
    pt_a2_mat = repmat(pt_a2,1,length(ind_in2));
    
    d_a1b1 = sum((pt_b1(:,ind_in2) - pt_a1_mat).^2,1);
    d_a1b2 = sum((pt_b2(:,ind_in2) - pt_a1_mat).^2,1);
    d_a2b1 = sum((pt_b1(:,ind_in2) - pt_a2_mat).^2,1);
    d_a2b2 = sum((pt_b2(:,ind_in2) - pt_a2_mat).^2,1);
    
    [val,ind_min] = min([d_a1b1; d_a1b2; d_a2b1; d_a2b2],[],1);

    % for closest endpts, compute midpoint
    for k = 1:length(ind_min),
        switch ind_min(k)
            case 1,
                1
                pt_intx(ind_in2(k)) = (pt_a1(1)+pt_b1(1,ind_in2(k)))./2;
                pt_inty(ind_in2(k)) = (pt_a1(2)+pt_b1(2,ind_in2(k)))./2;
            case 2,
                2
                pt_intx(ind_in2(k)) = (pt_a1(1)+pt_b2(1,ind_in2(k)))./2;
                pt_inty(ind_in2(k)) = (pt_a1(2)+pt_b2(2,ind_in2(k)))./2;
            case 3,
                3
                pt_intx(ind_in2(k)) = (pt_a2(1)+pt_b1(1,ind_in2(k)))./2;
                pt_inty(ind_in2(k)) = (pt_a2(2)+pt_b1(2,ind_in2(k)))./2;
            otherwise,
                4
                pt_intx(ind_in2(k)) = (pt_a2(1)+pt_b2(1,ind_in2(k)))./2;
                pt_inty(ind_in2(k)) = (pt_a2(2)+pt_b2(2,ind_in2(k)))./2;
        end
    end
end
    
pt_int = [pt_intx; pt_inty];