function [image_resource ErrorMsg] = CellCountingEvaluation(client_server, image_url, user, password) %(url, ImageID)
%[resources ErrorMsg ] = CellCountingEvaluation ( 'http://bodzio.ece.ucsb.edu:8080/ds/images/116','admin','admin' ) 

javaaddpath('../../lib/bisque.jar');
import bisque.*
ErrorMsg = '';
image_resource = '';
try
    %[im_data ErrorCode ErrorMsg] = getImageData(url, ImageID);
	%[im_tags ErrorCode ErrorMsg] = getImageTags(url, im_data);
    BQ = BQMatlab;
    BQ.login(user, password);
    BQ.initServers(client_server,client_server);
    image = BQ.loadImage(image_url);
    cell_N = char(BQ.findTag(image,'cellNumber'));
    if(isempty(cell_N)); error(char(BQError.getLastError())); end    
    cell_GT = char(BQ.findTag(image,'ManualCount_ONL'));
    if(isempty(cell_GT)); error(char(BQError.getLastError())); end    
    eval(['data = ',cell_GT,';']);
    data = mean(data);
    cell_GT = data;
     %cell_Tab=[];
    
    s=size(cell_GT);
    for i=1:s(1,1)
        %cell_Tab(i)=str2double(cell_GT(i,:));
        cell_Tab(i)=cell_GT(i,:);
    end
    errorN=eval_countingcell(str2double(cell_N), cell_Tab);
    %errorTag = addTag('cellError', num2str(error));
    %saveTag(url, ImageID, errorTag);

    errorTag = BQ.addTag(image,'Error_cellCounting',errorN);
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
