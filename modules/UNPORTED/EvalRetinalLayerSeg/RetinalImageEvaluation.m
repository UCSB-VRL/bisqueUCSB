function ErrorMsg = RetinalImageEvaluation(image_url, user, password)
javaaddpath('../../lib/bisque.jar');
import bisque.*
ErrorMsg = '';
init();
try
    %[im_data ErrorCode ErrorMsg] = getImageData(url, ImageID);
	%[im_tags ErrorCode ErrorMsg] = getImageTags(url, im_data);
    %[in_M Types ErrorCode ErrorMsg] = findTagValue(im_tags, 'mask');    
    %[in_GT Types ErrorCode ErrorMsg] = findTagValue(im_tags, 'groundTruth');
    BQ = BQMatlab;
    BQ.initServers(client_server,client_server);
    BQ.login(user, password);
    image = BQ.loadImage(image_url);        
    in_M = char(BQ.findTag(image, 'reference')); 
    if(isempty(in_M)); error(char(BQError.getLastError())); end  
    in_GT = char(BQ.findTag(image_url, 'groundTruth'));

    if(isempty(in_GT)); error(char(BQError.getLastError())); end  
    %[im2_data ErrorCode ErrorMsg] = getImageData(url, im1_reference);
    %im2 = readImage(url, im2_data, 'jpeg');

    
    
    
    %mask
    %[im_data ErrorCode ErrorMsg] = getImageData(url, in_M);
    %im_M = readImage(url, im_data, 'png');

    image = BQ.loadImage(in_M);
    im_M = uint8(BQ.loadImageData(image)); 
    if(isempty(im_M)); error(char(BQError.getLastError())); end  

    image = BQ.loadImage(in_GT);
    im_GT = uint8(BQ.loadImageData(image)); 
    if(isempty(im_GT)); error(char(BQError.getLastError())); end  
   
    [F_measure_region F_measure_boundary] = eval_segmentingretina(im_M,im_GT);

    %errorTag = addTag('retinalErrorR', num2str(F_measure_region));
    %saveTag(url, ImageID, errorTag);    
    %errorTag = addTag('retinalErrorB', num2str(F_measure_boundary));
    %saveTag(url, ImageID, errorTag);
    
    image = BQ.loadImage(image_url);    
    errorTag = BQ.addTag(image, 'retinalErrorR', F_measure_region);
    if(isempty(errorTag)); error(char(BQError.getLastError())); end  
    response = BQ.saveTag(image, errorTag);    
    if(isempty(response)); error(char(BQError.getLastError())); end  
    errorTag = BQ.addTag(image, 'retinalErrorB', F_measure_boundary);
    if(isempty(errorTag)); error(char(BQError.getLastError())); end  
    response = BQ.saveTag(image, errorTag);    
    if(isempty(response)); error(char(BQError.getLastError())); end  
    
    if(~strcmp(char(BQError.getLastError()),'')); error(char(BQError.getLastError())); end    
catch
    err = lasterror;
    ErrorMsg = err. message;
    return;
end
return
