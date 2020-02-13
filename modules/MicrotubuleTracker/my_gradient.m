function [gxx,gxy,gyy] = my_gradient(I)


gxx = [I(:,1),I(:,1:end-1)]+ [I(:,2:end),I(:,end)] - 2 * I;
gyy = [I(1,:);I(1:end-1,:)]+ [I(2:end,:);I(end,:)] - 2 * I;
gxy = [I(2:end,2:end),I(2:end,end); I(end,2:end) , I(end,end)]...
     +[I(1,1),I(1,1:end-1);I(1:end-1,1),I(1:end-1,1:end-1)]...
     -[I(1,2:end),I(1,end);I(1:end-1,2:end),I(1:end-1,end)]...
     -[I(2:end,1),I(2:end,1:end-1);I(end,1),I(end,1:end-1)];
gxy = gxy/4;