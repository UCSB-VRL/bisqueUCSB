function out = my_filter2(im,h)
len = size(h,1);
rep_size = (len-1)/2;
im2 = [im(1,1)*ones(rep_size),repmat(im(1,:),rep_size,1),im(1,end)*ones(rep_size);...
       repmat(im(:,1),1,rep_size),im,repmat(im(:,end),1,rep_size);...
       im(end,1)*ones(rep_size),repmat(im(end,:),rep_size,1),im(end,end)*ones(rep_size)];
out = filter2(h,im2,'full');
out = out (len:end-len+1,len:end-len+1);
