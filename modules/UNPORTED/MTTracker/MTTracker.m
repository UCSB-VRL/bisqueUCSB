
function [gobject_url ErrorMsg] = bqmttrace(client_server, mex_url, image_url, frame_number, user, password)

% the caller script is assumed to handles which frame to operate on
% this function operates on one frame at a time and writes the resulting
% track as a gobject, then returns the gobject_url to the script for
% processing the next frame if needed

% NOTE: right now we cannot read one frame at a time from the server (BO
% said he'll change the code for doing that) so, we're reading the entire
% image stack

% NOTE: this function writes the result to a gobject named "track result"
% it DOES NOT erase previously saved track results, so it must be handled
% in the calling script




% client_server = 'http://hammer.ece.ucsb.edu:8080';
% image_url = 'http://hammer.ece.ucsb.edu:8080/ds/images/5';
% user = 'admin';
% password = 'admin';
% frame_number = 1;

% %------------------------------------------------------------
% % write an initial set of trace points for testing
% gobj_track = BQ.createGObject('track','mt to be tracked');
% gobj_trace = BQ.createGObject('trace',num2str(frame_number));
% v = [156,290 ; 176,280];
% pred_path = trace_interp(v,3);
% BQ.addVertices(gobj_trace,pred_path);
% BQ.addGObject(gobj_track, gobj_trace);
% % write gobjects to database
% gobj_track_url = char(BQ.saveGObjectURL(image,gobj_track));
% %------------------------------------------------------------    



gobject_url = '';
ErrorMsg = '';

framenum = str2num(frame_number);

% path
warning off
javaaddpath('./bisque.jar');
%javaaddpath('../../lib/bisque.jar');
import bisque.*
warning off

try
    % setup service
    BQ = BQMatlab;
    BQ.initServers(client_server,client_server);
    BQ.login(user, password);
    
    mex = BQ.loadMEX(mex_url);
    resp = BQ.updateProgress(mex, 0);
    
    % get image from database
    image = BQ.loadImage([image_url '?view=deep']);
%    im = im2double(uint8(BQ.loadImageData(image)));
    im = im2double(uint8(BQ.loadImageDataParam(image,'depth=8,d')));

    resp = BQ.updateProgress(mex, 10);
    
    % read trace points

    % NOTE:
    % this part will have to be reworked for 
    % finding only the relevant gobjects (points)
    % from potentially many other ones

%    go_tracks = image.gobjects;
%    for i=0:size(go_tracks)-1
%        if strcmp(go_tracks.get(i).name,'mt to be tracked')
%            % read traces of each frame
%            vertices = go_tracks.get(i).gobjects.get(0).vertices;
%            for v=0:size(vertices)-1
%                index = vertices.get(v).index.intValue + 1;
%                x = vertices.get(v).x.doubleValue;
%                y = vertices.get(v).y.doubleValue;
%                ve(index,1) = x;
%                ve(index,2) = y;
%            end
%        end
%    end

     for ii = 0:mex.tags.size()-1
        T = mex.tags.get(ii);
        if strcmp(T.name,'$gobjects')
           go_tracks = T.gobjects;
        end
      end


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% changing from POINTS to the LAST POLYLINE on image
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
 
%    % we might have other gobjects that are not POINTS...
%    c = 1;
%    for i=0:size(go_tracks)-1
%        if strcmp(go_tracks.get(i).type,'point')  %  && ~(go_tracks.get(i).vertices.isEmpty)
%            ve(c,2) = go_tracks.get(i).vertices.get(0).x.doubleValue;
%            ve(c,1) = go_tracks.get(i).vertices.get(0).y.doubleValue;
%            c = c+1;
%            if c>2
%                break
%            end
%        end
%    end

     % we ll get the last polyline 
     c = 0;
     target_index = -1;
   
     for i=0:size(go_tracks)-1
         if strcmp(go_tracks.get(i).type,'polyline')
             uri_string = char(go_tracks.get(i).uri);
             gob_index = findstr(uri_string,'/gobjects/');
             gob_value = str2num(uri_string(gob_index+10:end));
             if gob_value > c
                 target_index = i;
                 c = gob_value;
             end
         end
     end

     if target_index > -1
        % read first and second index
        ve(1,2) = go_tracks.get(target_index).vertices.get(0).x.doubleValue;
        ve(1,1) = go_tracks.get(target_index).vertices.get(0).y.doubleValue;
        ve(2,2) = go_tracks.get(target_index).vertices.get(1).x.doubleValue;
        ve(2,1) = go_tracks.get(target_index).vertices.get(1).y.doubleValue; 
     else
        % no polyline found
        error('Please select a microtubule to track.');
     end


%    ve(1,1) = go_tracks.get(1).vertices.get(0).x.doubleValue;
%    ve(1,2) = go_tracks.get(1).vertices.get(0).y.doubleValue;
%    ve(2,1) = go_tracks.get(0).vertices.get(0).x.doubleValue;
%    ve(2,2) = go_tracks.get(0).vertices.get(0).y.doubleValue;

    ve = flipud(ve);

    myTrace = trace_interp(ve,3);

    Ix = myTrace(:,2);
    Iy = myTrace(:,1);    
    
    % run the tracker
    im = mat2gray(im);
    if mean(im(:))>0.5      % force image to be white tubes on black background
        im = 1-im;
    end


    % something wrong with compute_gradients? using older version
%    warning off
%    gradients = compute_gradients(im(:,:,framenum),[],[]);
%    if framenum == 1 || size(Ix,1) == 2
%        [a,b,thresh,my_path] = mt_track_init(im(:,:,framenum),gradients,Ix,Iy,'trackinvivo');
%    end
%    [a,b,thresh,my_path,pred_path] = mt_track(im(:,:,framenum+1),gradients,my_path,a,b,thresh,'trackinvivo');
%    resp = BQ.updateProgress(mex, 80);
%    warning on

    r = cell(size(im, 3), 1);
    try
      gradients = compute_gradients(im(:,:,1),[]);        
      [a,b,thresh,my_path] = mt_track_init(im(:,:,1),gradients,Ix,Iy,'trackinvivo');
      pred_path = my_path;
      r{1} = pred_path;
      for i=2:size(im,3)
        gradients = compute_gradients(im(:,:,i),[]);
        [a,b,thresh,my_path,pred_path] = mt_track(im(:,:,i),gradients,pred_path,a,b,thresh,'trackinvivo');
        r{i} = my_path;
        resp = BQ.updateProgress(mex, i);
      end
    catch
      % Is this how we end up with no tracks?
      err = lasterror;
      ErrorMsg = [ ErrorMsg err.message ] ;
    end
    


    % save mt track result
    
    % do we have previous results?
    prev_max_track_num = 0;
    prev_track_num = 0;
    prev_track = 0;
    for i=0:size(go_tracks)-1
        if strcmp(go_tracks.get(i).type,'track result')
            last_track_num = str2num(char(go_tracks.get(i).name));
            if prev_max_track_num < last_track_num
                prev_max_track_num = last_track_num;
                prev_track = 1;
            end
        end
    end
    if prev_track
        prev_track_num = prev_max_track_num + 1;
    end


    %% 
    if isempty(r{2}) 
      % Then no tracks were found ...
      % r{1} always has initial points, but no points found beyond.
 
    else 
  

     % write the new track
     gobj_track = BQ.createGObject('track result',num2str(prev_track_num));
%    gobj_trace = BQ.createGObject('polyline',frame_number);
%    BQ.addVertices(gobj_trace,[pred_path zeros(size(pred_path,1),1) ones(size(pred_path,1),framenum)]);
%     BQ.addGObject(gobj_track, gobj_trace);
 
     for i=1:length(r)
         if ~isempty(r{i})
           gobj_trace = BQ.createGObject('polyline',num2str(i));
           BQ.addVertices(gobj_trace,[fliplr(r{i}) zeros(size(r{i},1),1) ones(size(r{i},1),1)*(i-1)]);
           BQ.addGObject(gobj_track,gobj_trace);
         end
     end

    gobject_url = char(BQ.saveGObjectURL(image,gobj_track));
   end

    %resp = BQ.updateProgress(mex, 100);
    % % send image to database
    % new_image = BQ.initImage(size(im,1), size(im,2), 1, 30, 1, 8, 'uint8', 1);
    % new_image_url = BQ.saveImage(new_image, uint8(im));

    BQ.addTag (mex, 'gobject_url', gobject_url);
    BQ.finished(mex, '');
catch
    err = lasterror;
    ErrorMsg = [ErrorMsg err.message ', '];
    for i=1:size(err.stack,1)
        ErrorMsg = [ErrorMsg err.stack(i,1).file ',' err.stack(i,1).name ',' num2str(err.stack(i,1).line) ','];
    end
    fprintf('Exception: %s', ErrorMsg);
    BQ.failed(mex, ErrorMsg);
    return;
end




