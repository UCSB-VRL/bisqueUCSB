function ErrorMsg = MTTrackingEvaluation(client_server, image_url, user, password)
%client_server='http://bodzio.ece.ucsb.edu:8080';
%image_url='http://bodzio.ece.ucsb.edu:8080/ds/images/5051';
%user='admin'; password='admin';MT.expert='ONL';

%INPUT: image_url of input image to be traced and compared to ground
%       mt_ gobject
%truth
ErrorMsg = '';
javaaddpath('../../lib/bisque.jar');
import bisque.*

%% Path
%CHANGE HERE THE PATH:
% javaaddpath('Z:\Elisa\PostImagetoBisquick\Statistcs\interface_V2');
% addpath Z:\Elisa\PostImagetoBisquick\UploadRetina\Retina_code
% addpath Z:\Elisa\PostImagetoBisquick\UploadMicrotubule\code
%% MAIN

%%VAR
try


    BQ = BQMatlab;
    BQ.initServers(client_server,client_server);
    BQ.login(user, password);
    image = BQ.loadImage(image_url);
    MT.image = uint8(BQ.loadImageData(image)); 

    if(isempty(MT.image)); error(char(BQError.getLastError())); end 
    response = BQXMLgetText([image_url,'/gobjects/?view=deep']);
    if(isempty(response)); error(char(BQError.getLastError())); end 
    V = xml_parseany(char(response));

    %% Load
    %load MT ground truth and MT tracing results
    MT.gt_track=MT_loadgtdata(V);
    MT.track=MT_loadMTdata(V);


    %%
    %%Evaluate the results
    MT_evaluate_error()

    %%
    %%Save
    MT_save_evaluation(image_url)
    %%

    if(~strcmp(char(BQError.getLastError()),'')); error(char(BQError.getLastError())); end  
catch
    err = lasterror;
    ErrorMsg =err. message;
    return;
end


    function gt_track_all=MT_loadgtdata(V)

        num_traces=length(V.gobject)-1;

        % Choose expert
        MT.expert={'corey','greg','nicholas','stephanie'};

        %read the ground truth
        num_experts=length(V.gobject{1}.gobject)/num_traces;
        num_frame=length(V.gobject{1}.gobject{1}.polyline);
        MT.num_frame=num_frame;
        gt_track=cell(num_frame,1);
        for i=1:num_frame
            gt_track{i}=cell(1,num_traces);
        end

        expert=0;
        for offset=0:num_traces:num_traces*3  %stephanie, corey,nicholas, greg
            expert=1+expert;
            for tube_id=1:num_traces
                %V.gobject{1}.gobject{ii}
                for frame=1:num_frame
                    num_points = length(V.gobject{1}.gobject{tube_id+offset}.polyline{frame}.vertex);
                    my_path = zeros(num_points,2);
                    for i = 1:num_points
                        vertex = V.gobject{1}.gobject{tube_id+offset}.polyline{frame}.vertex{i};
                        my_path(i,2) = str2double(vertex.ATTRIBUTE.x)+1;
                        my_path(i,1) = str2double(vertex.ATTRIBUTE.y)+1;
                    end
                    gt_track_all{frame}{tube_id}{expert}=my_path;
                end
            end
        end

    end



    function track=MT_loadMTdata(V)

        num_traces=length(V.gobject)-1;

        num_frame=MT.num_frame-2;
        track=cell(num_frame,1);
        for i=1:num_frame
            track{i}=cell(1,num_traces);
        end
        for tube_id=1:num_traces
            %V.gobject{1}.gobject{ii}
            num_frame=length(V.gobject{tube_id+1}.polyline);
            frame=1;
            while frame<=num_frame
                %%ADD IF FRAME < NUM_FRAME
                num_points = length(V.gobject{tube_id+1}.polyline{frame}.vertex);
                my_path = zeros(num_points,2);
                for i = 1:num_points
                    vertex = V.gobject{tube_id+1}.polyline{frame}.vertex{i};
                    my_path(i,2) = str2double(vertex.ATTRIBUTE.x)+1;
                    my_path(i,1) = str2double(vertex.ATTRIBUTE.y)+1;
                end
                track{frame}{tube_id}=my_path;
                frame=frame+1;
            end
        end

    end

    function MT_evaluate_error()


        %PARAMETERS
        % these thresholds and weights are subject to change
        % see comments in f_trace_error1 for details
        weight1=.85; weight2=.10; weight3=.05;
        threshold1=6;threshold2=3; threshold3=.15;

        % initializations
        microtubule_matrix=[];
        microtubule_matrix1=[];
        microtubule_matrix2=[];
        microtubule_matrix3=[];
        microtubule_matrix4=[];
        gt_trace = MT.gt_track;
        %load tracing algorithm's output (trace)
        mt_trace_output = MT.track;




        % run through all tracks in each file
        for track_id = 1:length(gt_trace{1})

            % run through all frames in each track
            for frame_num = 3:length(gt_trace)

                % check number of points in trace output and ground truth
                if ~isempty(mt_trace_output{frame_num-2}{track_id})
                    %                 stack_name_list{end+1}=name;
                    %                 frame_id_list(end+1) = frame_num;
                    %                 track_id_list(end+1) = track_id;

                    % CHANGE HERE TO GETIMAGE DATA
                    image=MT.image(:,:,frame_num); %QUESTION SHOULD WE
                    %NORMALIZE THE IMAGES??
                    %image=imread([stack_dir,stack_name1],frame_num);


                    % microtubule vector contains:
                    % [tip_distance,average_distance,max_distance,length_gt,length_trace, ...
                    % diff,percent_diff,hausdorff_distance,error]
                    gt_tip_end=zeros(1,2);
                    for expert=1:4
                        gt_tip_end=gt_tip_end+(gt_trace{frame_num}{track_id}{expert}(end,:));
                    end
                    gt_tip_end=gt_tip_end/4;

                    tip_distance_fused=f_tip_distance(gt_tip_end, mt_trace_output{frame_num-2}{track_id}(end,:));

                    [microtubule_vector_expert1]=f_getstats_one_microtubule(...
                        gt_trace{frame_num}{track_id}{1}(:,:), mt_trace_output{frame_num-2}{track_id}(:,:),...
                        image,threshold1,threshold2,threshold3,weight1,weight2,weight3);
                    [microtubule_vector_expert2]=f_getstats_one_microtubule(...
                        gt_trace{frame_num}{track_id}{2}(:,:), mt_trace_output{frame_num-2}{track_id}(:,:),...
                        image,threshold1,threshold2,threshold3,weight1,weight2,weight3);
                    [microtubule_vector_expert3]=f_getstats_one_microtubule(...
                        gt_trace{frame_num}{track_id}{3}(:,:), mt_trace_output{frame_num-2}{track_id}(:,:),...
                        image,threshold1,threshold2,threshold3,weight1,weight2,weight3);
                    [microtubule_vector_expert4]=f_getstats_one_microtubule(...
                        gt_trace{frame_num}{track_id}{4}(:,:), mt_trace_output{frame_num-2}{track_id}(:,:),...
                        image,threshold1,threshold2,threshold3,weight1,weight2,weight3);
                    % creates a matrix with file# track# frame# and all
                    % components of microtubule_vector
                    microtubule_matrix1(end+1, :)=[track_id, frame_num, microtubule_vector_expert1];
                    microtubule_matrix2(end+1, :)=[track_id, frame_num, microtubule_vector_expert2];
                    microtubule_matrix3(end+1, :)=[track_id, frame_num, microtubule_vector_expert3];
                    microtubule_matrix4(end+1, :)=[track_id, frame_num, microtubule_vector_expert4];
                    microtubule_matrix(end+1, :)=[track_id, frame_num,tip_distance_fused];
                else
                    microtubule_vector_expert1=ones(1,13);
                    microtubule_matrix1(end+1, :)=[track_id, frame_num, microtubule_vector_expert1];
                    microtubule_matrix2(end+1, :)=[track_id, frame_num, microtubule_vector_expert1];
                    microtubule_matrix3(end+1, :)=[track_id, frame_num, microtubule_vector_expert1];
                    microtubule_matrix4(end+1, :)=[track_id, frame_num, microtubule_vector_expert1];
                    tip_distance_fused=NaN;
                    microtubule_matrix(end+1, :)=[track_id, frame_num,tip_distance_fused];
                end
            end
        end

        MT.p_ct_fused=numel(find(microtubule_matrix(:,3)>threshold1))/size(microtubule_matrix,1);

        MT.error1=numel(find(microtubule_matrix1(:,13)==1 | (microtubule_matrix1(:,14)==1) | (microtubule_matrix1(:,15)==1)))/size(microtubule_matrix1,1);
        MT.p_ct1=sum(microtubule_matrix1(:,13))/size(microtubule_matrix1,1);
        MT.p_cb1=sum(microtubule_matrix1(:,14))/size(microtubule_matrix1,1);
        MT.p_cl1=sum(microtubule_matrix1(:,15))/size(microtubule_matrix1,1);

        MT.error2=numel(find(microtubule_matrix2(:,13)==1 | (microtubule_matrix2(:,14)==1) | (microtubule_matrix2(:,15)==1)))/size(microtubule_matrix2,1);
        MT.p_ct2=sum(microtubule_matrix2(:,13))/size(microtubule_matrix2,1);
        MT.p_cb2=sum(microtubule_matrix2(:,14))/size(microtubule_matrix2,1);
        MT.p_cl2=sum(microtubule_matrix2(:,15))/size(microtubule_matrix2,1);

        MT.error3=numel(find(microtubule_matrix3(:,13)==1 | (microtubule_matrix3(:,14)==1) | (microtubule_matrix3(:,15)==1)))/size(microtubule_matrix3,1);
        MT.p_ct3=sum(microtubule_matrix3(:,13))/size(microtubule_matrix3,1);
        MT.p_cb3=sum(microtubule_matrix3(:,14))/size(microtubule_matrix3,1);
        MT.p_cl3=sum(microtubule_matrix3(:,15))/size(microtubule_matrix3,1);

        MT.error4=numel(find(microtubule_matrix4(:,13)==1 | (microtubule_matrix4(:,14)==1) | (microtubule_matrix4(:,15)==1)))/size(microtubule_matrix4,1);
        MT.p_ct4=sum(microtubule_matrix4(:,13))/size(microtubule_matrix4,1);
        MT.p_cb4=sum(microtubule_matrix4(:,14))/size(microtubule_matrix4,1);
        MT.p_cl4=sum(microtubule_matrix4(:,15))/size(microtubule_matrix4,1);


    end

    function MT_save_evaluation(image_url)

        evaluation_output_text = ['<tag name="MTTrackingEvaluation Output">'];
        evaluation_output_text = [evaluation_output_text,'<tag name="fused tip error" value="',num2str(MT.p_ct_fused),'"/>'];

        evaluation_output_text = [evaluation_output_text,'<tag name="Expert" value="',MT.expert{1},'">'];
        evaluation_output_text = [evaluation_output_text,'<tag name="tip distance" value="',num2str(MT.p_ct1),'"/>'];
        evaluation_output_text = [evaluation_output_text,'<tag name="length distance" value="',num2str(MT.p_cl1),'"/>'];
        evaluation_output_text = [evaluation_output_text,'<tag name="body distance" value="',num2str(MT.p_cb1),'"/>'];
        evaluation_output_text = [evaluation_output_text,'<tag name="error measure" value="',num2str(MT.error1),'"/>'];
        evaluation_output_text = [evaluation_output_text,'</tag>'];

        evaluation_output_text = [evaluation_output_text,'<tag name="Expert" value="',MT.expert{2},'">'];
        evaluation_output_text = [evaluation_output_text,'<tag name="tip distance" value="',num2str(MT.p_ct2),'"/>'];
        evaluation_output_text = [evaluation_output_text,'<tag name="length distance" value="',num2str(MT.p_cl2),'"/>'];
        evaluation_output_text = [evaluation_output_text,'<tag name="body distance" value="',num2str(MT.p_cb2),'"/>'];
        evaluation_output_text = [evaluation_output_text,'<tag name="error measure" value="',num2str(MT.error2),'"/>'];
        evaluation_output_text = [evaluation_output_text,'</tag>'];


        evaluation_output_text = [evaluation_output_text,'<tag name="Expert" value="',MT.expert{3},'">'];
        evaluation_output_text = [evaluation_output_text,'<tag name="tip distance" value="',num2str(MT.p_ct3),'"/>'];
        evaluation_output_text = [evaluation_output_text,'<tag name="length distance" value="',num2str(MT.p_cl3),'"/>'];
        evaluation_output_text = [evaluation_output_text,'<tag name="body distance" value="',num2str(MT.p_cb3),'"/>'];
        evaluation_output_text = [evaluation_output_text,'<tag name="error measure" value="',num2str(MT.error3),'"/>'];
        evaluation_output_text = [evaluation_output_text,'</tag>'];

        evaluation_output_text = [evaluation_output_text,'<tag name="Expert" value="',MT.expert{4},'">'];
        evaluation_output_text = [evaluation_output_text,'<tag name="tip distance" value="',num2str(MT.p_ct4),'"/>'];
        evaluation_output_text = [evaluation_output_text,'<tag name="length distance" value="',num2str(MT.p_cl4),'"/>'];
        evaluation_output_text = [evaluation_output_text,'<tag name="body distance" value="',num2str(MT.p_cb4),'"/>'];
        evaluation_output_text = [evaluation_output_text,'<tag name="error measure" value="',num2str(MT.error4),'"/>'];
        evaluation_output_text = [evaluation_output_text,'</tag>'];



        evaluation_output_text = [evaluation_output_text,'</tag>'];
        response = BQXML.postText([image_url,'/tags'],evaluation_output_text);
        if(isempty(response)); error(char(BQError.getLastError())); end 

    end

end
