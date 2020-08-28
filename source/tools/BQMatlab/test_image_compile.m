imurl = 'http://bisque.ece.ucsb.edu/data_service/image/161855';

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% using bq.Image
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% fetch image into a file using its original name
image = bq.Factory.fetch(imurl);
filename = image.fetch([]);

