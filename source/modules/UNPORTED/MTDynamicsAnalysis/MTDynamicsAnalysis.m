% clear; close all; clc;
% image_url = 'http://hammer.ece.ucsb.edu:9090/ds/images/85';
% user = 'admin';
% password = 'admin';
% 
% growth_rate = '3';
% growth_len = '0.3';
% short_rate = '4';
% short_len  = '0.5';
% atten_dur='5';
% track_info = 'no name';

function [image_resource ErrorMsg] =  MTDynamicsAnalysis(client_server, image_url, growth_rate, growth_len,short_rate , short_len, atten_dur , track_info ,user, password)

% Protocol to talk to bisquik
init();


ErrorMsg = '';
image_resource = '';

try
    BQ = BQMatlab;
    BQ.initServers(client_server,client_server);
    BQ.login(user, password);
    image = BQ.loadImage(image_url); 
    response = BQXMLgetText([image_url,'/gobjects?view=deep']);
    if(isempty(response)); error(char(BQError.getLastError())); end    
    v = xml_parseany(char(response));

    mt_track_gobject = [];

    num_gobjects = length(v.gobject);
    for i = 1:num_gobjects
        if strcmp(v.gobject{i}.ATTRIBUTE.name,track_info) && strcmp(v.gobject{i}.ATTRIBUTE.type,'mttrack')
            mt_track_gobject = v.gobject{i};
            break;
        end
    end

    if isempty(mt_track_gobject)
        error('no mttrack file found\n');
    end

    origin_pt = zeros(1,2);


    origin_pt(1,1) = str2double(mt_track_gobject.point{1}.vertex{1}.ATTRIBUTE.x);
    origin_pt(1,2) = str2double(mt_track_gobject.point{1}.vertex{1}.ATTRIBUTE.y);


    num_points = length(mt_track_gobject.polyline{1}.vertex);

    points = zeros(num_points,2);
    frames = zeros(num_points,1);

    for i = 1:num_points
        vertex = mt_track_gobject.polyline{1}.vertex{i};
        points(i,1) = str2double(vertex.ATTRIBUTE.x);
        points(i,2) = str2double(vertex.ATTRIBUTE.y);
        frames(i) = str2double(vertex.ATTRIBUTE.t);
    end

    length_series = sqrt(sum((points-repmat(origin_pt,num_points,1)).^2,2));
    time_series = frames*4;
    length_series = length_series * str2double(char(BQ.findTag(image,'pixel_resolution_x_y')));
    if(isempty(length_series)); error(char(BQError.getLastError())); end
    time_length_series = [ time_series,length_series];



    params.growth_rate = str2double(growth_rate);
    params.growth_len = str2double(growth_len);
    params.short_rate = -str2double(short_rate);
    params.short_len = -str2double(short_len);
    params.atten_dur = str2double(atten_dur);

    %fprintf('%f\n',params.growth_rate);


    [start_end_times,labels] = segment_length_series(time_length_series,params);


    time_length_str = sprintf('[');
    for i = 1:size(time_length_series,1)
        time_length_str=[time_length_str,sprintf('%.1f,%.1f;',time_length_series(i,1),...
            time_length_series(i,2))];
    end
    time_length_str=[time_length_str,sprintf(']')];


    start_end_time_str = sprintf('{');
    for i = 1:size(start_end_times,1)
        start_end_time_str=[start_end_time_str,sprintf('%.1f,%.1f;',time_length_series(start_end_times(i,1),1),...
            time_length_series(start_end_times(i,2),1))];
    end
    start_end_time_str=[start_end_time_str,sprintf('}')];

    label_str = sprintf('(');
    for i = 1:length(labels)
        label_str=[label_str,sprintf('%c,',upper(labels{i}))];
    end
    label_str=[label_str,sprintf(')')];

    analysis_output_text = ['<tag name="MTDynamicsAnalysis Output">'];
    analysis_output_text = [analysis_output_text,'<tag name="track_info" value="',track_info,'"/>'];
    analysis_output_text = [analysis_output_text,'<tag name="timeLengthSeries" value="',time_length_str,'"/>'];
    analysis_output_text = [analysis_output_text,'<tag name="startEndTimes" value="',start_end_time_str,'"/>'];
    analysis_output_text = [analysis_output_text,'<tag name="label" value="',label_str,'"/>'];
    analysis_output_text = [analysis_output_text,'</tag>'];
    response = BQXML.postText([image_url,'/tags'],analysis_output_text);
    if(isempty(response)); error(char(BQError.getLastError())); end
    if(~strcmp(char(BQError.getLastError()),'')); error(char(BQError.getLastError())); end  
catch
    err = lasterror;
    ErrorMsg =err. message;
    return;
end
