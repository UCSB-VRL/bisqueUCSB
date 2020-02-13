
function [Iy_new,Ix_new] = project_to_tube(Ix,Iy,Vx,Vy,gxx,gxy,gyx,gyy,d)
k=1;
y0 = round(Iy+(d-k)*Vy);
x0 = round(Ix+(d-k)*Vx);
y1 = round(Iy-(d-k)*Vy);
x1 = round(Ix-(d-k)*Vx);
[search_path,I] = get_search_path(size(gxx),x0,y0,x1,y1);

if ~isempty(I)


%     my_angle = atan(Vy/(Vx+1e-6));
%     GG = [gxx(I),gxy(I),gyx(I),gyy(I)];
%     gg = [cos(my_angle)^2;
%         cos(my_angle)*sin(my_angle);
%         cos(my_angle)*sin(my_angle);
%         sin(my_angle)^2];
% 
%     second_ds = abs(GG*gg);
    second_ds = zeros(size(I));
    for i = 1:length(I)
    h = [gxx(I(i)),gxy(I(i));gyx(I(i)),gyy(I(i))];
    [eig_vec,eig_val] = eig(h);
    second_ds(i) = abs(eig_val(1,1));
    end

    [max_val,max_ind] = max(second_ds);

    Iy_new = search_path(max_ind,1);
    Ix_new = search_path(max_ind,2);


else
    Iy_new = [];
    Ix_new = [];
end
