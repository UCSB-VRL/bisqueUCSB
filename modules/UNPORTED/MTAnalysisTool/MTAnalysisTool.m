function ErrorMsg = MTAnalysisTool(image_url, tag_name,...
						Simple_Growth_Rate, Simple_Growth_Length, ...
 						Simple_Shortening_Rate, Simple_Shortening_Length, ...
						Simple_Attenuation_Time, Simple_Attenuation_Length, ...
						Complex_Growth_Rate, Complex_Growth_Length, ...
						Complex_Shortening_Rate, Complex_Shortening_Length, ...
						Complex_Attenuation_Time, Complex_Attenuation_Length, ...
						user, password)

ErrorMsg = '';
% Program: Microtubule Dynamics Analysis 
%   Copyright 2007 Boguslaw Obara <obara@ece.ucsb.edu>
%   http://boguslawobara.net
%
% Help: 

% Versions:
%   v1.0 - 13/09/2007 
%       - first implementation    

% Co-authors:
%   Arnab Bhattacharya <arnab@cs.ucsb.edu> 
%        Java Package for microtubule events analysis

%% Path
irtdir = which('MTAnalysisTool.m');
[irtdir dummy] = fileparts(irtdir);
clear dummy;
path([irtdir '/lib'], path)
disp(['Adding to java path ' [irtdir '/lib']]);
javaaddpath([irtdir '/lib']);
javaaddpath('../../lib/bisque.jar');
import bisque.*
%% Clear
clc; close all;
%% MAIN
try 
    mt.image_url=image_url;
    if strcmp(tag_name,'tag_name')>0
        mt.tag_name='data';
    else
        mt.tag_name=tag_name;
    end
    mt.user=user;
    mt.password=password;
    mt.cell_data={};
    mt.cell_data2={};
    mt.range=[];
    mt.range_str=[];
    %initialization();
	initializationT(...						
						Simple_Growth_Rate, Simple_Growth_Length, ...
 						Simple_Shortening_Rate, Simple_Shortening_Length, ...
						Simple_Attenuation_Time, Simple_Attenuation_Length, ...
						Complex_Growth_Rate, Complex_Growth_Length, ...
						Complex_Shortening_Rate, Complex_Shortening_Length, ...
						Complex_Attenuation_Time, Complex_Attenuation_Length);
    mt_load();
    mt_run();
    mt_fill_table(mt.data_x,mt.data_y,mt.range);
    mt_calculate_table2(mt.cell_data, length(mt.data_x)-1);
    mt_save_d();
    %mt_plotImage();
    if(~strcmp(char(BQError.getLastError()),'')); error(char(BQError.getLastError())); end 
catch 
    err = lasterror;
    ErrorMsg =err. message;
    return;
end
%% PlotImage
function mt_plotImage()
    mt.data_x=mt.data(:,2);
    mt.data_y=mt.data(:,1);
    X = mt_plot(mt.data_x,mt.data_y,mt.range);
    size_im = size(X);
end
%% PlotImage
function X = mt_plot(data_x,data_y,range)
    for i=1:length(range)
        c='r';
        if range(i,1)==0
            c='r';
        elseif range(i,1)==1
            c='b';
        elseif range(i,1)==2
            c='g';
        elseif range(i,1)==3
            c='k';
        end
        plot(data_x(range(i,2):range(i,3)),data_y(range(i,2):range(i,3)),'-s','LineWidth',1,...
            'Color',c,'MarkerFaceColor',c,'MarkerSize',2);
        hold on
    end
    %gridxy(data_x(range(i,2):range(i,3)),'Color','r','Linestyle',':') ;
    F = getframe(gcf);
    [X,Map] = frame2im(F);
    close all;
end
%% Initialization
function mt_loadintoDB()
    data_str = '[4.018000,4.250728;8.007000,4.885783;12.010000,5.054066;16.010000,5.985294;20.010000,7.388463;24.010000,7.574776;28.010000,7.574776;32.010000,5.798993;36.010000,7.005955;40.010000,8.232822;44.010000,9.625145;48.010000,8.506578;52.010000,5.700505;56.009000,6.722935;60.009000,8.120951;64.010000,9.625145;68.010000,10.022443;72.010000,9.836436;76.010000,10.123634;80.010000,9.751933;84.010000,10.616772;88.010000,10.560000;92.010000,9.875329;96.010000,9.177560;100.021000,5.886963;104.010000,3.855214;]';
    image_url = 'http://bodzio.ece.ucsb.edu:8080/ds/images/133';
    user = 'admin';
    password = 'admin';
    BQ = BQMatlab;
    BQ.initServers(client_server,client_server);
    BQ.login(user, password);
    image = BQ.loadImage(image_url);
    tag = BQ.addTag(image,'data', data_str');
    BQ.saveTag(image, tag);  

end
function initializationT(...						
						Simple_Growth_Rate, Simple_Growth_Length, ...
 						Simple_Shortening_Rate, Simple_Shortening_Length, ...
						Simple_Attenuation_Time, Simple_Attenuation_Length, ...
						Complex_Growth_Rate, Complex_Growth_Length, ...
						Complex_Shortening_Rate, Complex_Shortening_Length, ...
						Complex_Attenuation_Time, Complex_Attenuation_Length)
    mt.param(1)=str2double(Simple_Growth_Rate);
    mt.param(2)=str2double(Simple_Growth_Length);
    mt.param(3)=str2double(Complex_Growth_Rate);
    mt.param(4)=str2double(Complex_Growth_Length);
    mt.param(5)=str2double(Simple_Shortening_Rate);
    mt.param(6)=str2double(Simple_Shortening_Length);
    mt.param(7)=str2double(Complex_Shortening_Rate);
    mt.param(8)=str2double(Complex_Shortening_Length);
    mt.param(9)=str2double(Simple_Attenuation_Time);
    mt.param(10)=str2double(Simple_Attenuation_Length);
    mt.param(11)=str2double(Complex_Attenuation_Time);
    mt.param(12)=str2double(Complex_Attenuation_Length);
end
%% Initialization
function initialization()
    C=Constants;
    mt.param(1)=C.SIMPLE_GROWTH_RATE;
    mt.param(2)=C.SIMPLE_GROWTH_LENGTH;
    mt.param(3)=C.COMPLEX_GROWTH_RATE;
    mt.param(4)=C.COMPLEX_GROWTH_LENGTH;
    mt.param(5)=C.SIMPLE_SHORTENING_RATE;
    mt.param(6)=C.SIMPLE_SHORTENING_LENGTH;
    mt.param(7)=C.COMPLEX_SHORTENING_RATE;
    mt.param(8)=C.COMPLEX_SHORTENING_LENGTH;
    mt.param(9)=C.SIMPLE_ATTENUATION_TIME;
    mt.param(10)=C.SIMPLE_ATTENUATION_LENGTH;
    mt.param(11)=C.COMPLEX_ATTENUATION_TIME;
    mt.param(12)=C.COMPLEX_ATTENUATION_LENGTH;
    mt.param=mt.param';
end
%% Fill table
function mt_fill_table(data_x,data_y,range)
    mt.cell_data=cell(length(data_x),5);
    for i=1:length(data_x)-1
        mt.cell_data{i,1}=i;
        mt.cell_data{i,2}=data_y(i+1)-data_y(i); 
        mt.cell_data{i,3}=(data_x(i+1)-data_x(i))/60.0; 
    end
    for i=1:length(data_x)-1
        mt.cell_data{i,4}=(data_y(i)-data_y(i+1))/(data_x(i)-data_x(i+1));         
        mt.cell_data{i,4}=(data_y(i)-data_y(i+1))/((data_x(i)-data_x(i+1))/60.0);         
    end
    
    s=size(range(:,1));
    for i=1:s(1,1)
        if range(i,3)==length(data_x), range(i,3)=length(data_x)-1; end;
        mt.cell_data(range(i,2):range(i,3),5)={range(i,1)};
    end
end
%% Calculate table 2
function mt_calculate_table2(cell_data, size)
    i_s0 = 1;
    i_s1 = 1;
    i_s2 = 1;
    i_s3 = 1;   
    %cell_data=num2cell(cell_data);
    %mt.cell_data2(1:50,1:11)={0};
    i=1;    
    while(i<size-1)
        if(cell_data{i,5}==cell_data{i+1,5})
            index=0; value(1)=0; value(2)=0; value(3)=0; 
            while(cell_data{i,5}==cell_data{index+i,5})
                value(1)=value(1)+cell_data{index+i,2};
                value(2)=value(2)+cell_data{index+i,3};
                value(3)=value(3)+cell_data{index+i,4};
                index=index + 1;
                
            end
            %i=i-1;
            if(cell_data{i,5}==0)
               mt.cell_data2{i_s0,2}=value(1);
               mt.cell_data2{i_s0,3}=value(2);
               mt.cell_data2{i_s0,4}=value(3)/index;
               i_s0=i_s0+1; 
            elseif(cell_data{i,5}==1)
               mt.cell_data2{i_s1,5}=value(1);
               mt.cell_data2{i_s1,6}=value(2);
               mt.cell_data2{i_s1,7}=value(3)/index;
               i_s1=i_s1+1;                
            elseif(cell_data{i,5}==2)
               mt.cell_data2{i_s2,8}=value(1);
               mt.cell_data2{i_s2,9}=value(2);
               mt.cell_data2{i_s2,10}=value(3)/index;
               i_s2=i_s2+1;                
            end
            i=i+index;     
            if(i<size+1)
                if(cell_data{i-1,5}==0 && cell_data{i,5}==1)
                    mt.cell_data2{i_s3,11}='xC';
                    i_s3=i_s3+1;
                elseif(cell_data{i-1,5}==2 && cell_data{i,5}==1)                
                    mt.cell_data2{i_s3,11}='xC';
                    i_s3=i_s3+1;
                elseif(cell_data{i-1,5}==1 && cell_data{i,5}==2)
                    mt.cell_data2{i_s3,11}='xR';
                    i_s3=i_s3+1;
                elseif(cell_data{i-1,5}==1 && cell_data{i,5}==0)     
                    mt.cell_data2{i_s3,11}='xR';                
                    i_s3=i_s3+1;
                end         
            end
        else
            if(cell_data{i,5}==0)
               mt.cell_data2{i_s0,2}=cell_data{i,2};
               mt.cell_data2{i_s0,3}=cell_data{i,3};
               mt.cell_data2{i_s0,4}=cell_data{i,4};
               i_s0=i_s0+1; 
            elseif(cell_data{i,5}==1)
               mt.cell_data2{i_s1,5}=cell_data{i,2};
               mt.cell_data2{i_s1,6}=cell_data{i,3};
               mt.cell_data2{i_s1,7}=cell_data{i,4};
               i_s1=i_s1+1;             
            elseif(cell_data{i,5}==2)
               mt.cell_data2{i_s2,8}=cell_data{i,2};
               mt.cell_data2{i_s2,9}=cell_data{i,3};
               mt.cell_data2{i_s2,10}=cell_data{i,4};
               i_s2=i_s2+1; 
            end
            if(cell_data{i,5}==0 && cell_data{i+1,5}==1)
                mt.cell_data2{i_s3,11}='C';
                i_s3=i_s3+1;
            elseif(cell_data{i,5}==2 && cell_data{i+1,5}==1)                
                mt.cell_data2{i_s3,11}='C';
                i_s3=i_s3+1;
            elseif(cell_data{i,5}==1 && cell_data{i+1,5}==2)
                mt.cell_data2{i_s3,11}='R';
                i_s3=i_s3+1;
            elseif(cell_data{i,5}==1 && cell_data{i+1,5}==0)     
                mt.cell_data2{i_s3,11}='R';                
                i_s3=i_s3+1;
            end
            i=i+1;
        end
    end
    
    mt.max_v = max([i_s0, i_s1, i_s2 , i_s3]);
    i=1;
    while(i<mt.max_v)
        mt.cell_data2{i,1}=i;
        i=i+1;
    end
end
%% RUN
function mt_run()
    T=TrackEvent();
    T.choice = 2;    
    T.start(mt.data, mt.param(:,1));
    mt.range=T.getEvents();
    mt.range(:,2:3)=mt.range(:,2:3)+1;    
    mt.range_str=mt_range(mt.range);
    mt.data_x=mt.data(:,2);
    mt.data_y=mt.data(:,1);    
end
%% Range as letters
function range_str=mt_range(range)
    range_str=[];
    for i=1:length(range)
        c='r';
        if range(i,1)==0
            c='r';
        elseif range(i,1)==1
            c='b';
        elseif range(i,1)==2
            c='g';
        elseif range(i,1)==3
            c='k';
        end
        range_str=[range_str; c];
    end
end
%% Load
function mt_load()
    data = [];
    BQ = BQMatlab;

    BQ.login(mt.user, mt.password);
    image = BQ.loadImage(mt.image_url);
    tag = char(BQ.findTag(image, mt.tag_name));
    %tag = '[4.018000,4.250728;8.007000,4.885783;12.010000,5.054066;16.010000,5.985294;20.010000,7.388463;24.010000,7.574776;28.010000,7.574776;32.010000,5.798993;36.010000,7.005955;40.010000,8.232822;44.010000,9.625145;48.010000,8.506578;52.010000,5.700505;56.009000,6.722935;60.009000,8.120951;64.010000,9.625145;68.010000,10.022443;72.010000,9.836436;76.010000,10.123634;80.010000,9.751933;84.010000,10.616772;88.010000,10.560000;92.010000,9.875329;96.010000,9.177560;100.021000,5.886963;104.010000,3.855214;]';
    eval(['data = ',tag,';']);
    mt.data=mt_data_update(data);
end
%% Length
function data_out=mt_data_update(data)
    data_out(:,1)=data(:,2);
    data_out(:,2)=data(:,1);
end
%% Save
function mt_save_d()
    BQ = BQMatlab;
    BQ.login(mt.user, mt.password);
    image = BQ.loadImage(mt.image_url);

    start_end_range_str = sprintf('[');
    for i = 1:size(mt.range,1)
        start_end_range_str=[start_end_range_str,sprintf('%f,%f;',mt.data(mt.range(i,2),1),...
            mt.data(mt.range(i,3),1))];
    end
    start_end_range_str=[start_end_range_str,sprintf(']')];

    startEndRangeTags = BQ.addTag(image, 'ranges', start_end_range_str);
    BQ.saveTag(image, startEndRangeTags);
    range_str = sprintf('[');
    for i = 1:length(mt.range_str)
        range_str=[range_str,sprintf('''%c'';',mt.range_str(i))];
    end
    range_str=[range_str,sprintf(']')];

    rangeTags = BQ.addTag(image, 'labels',range_str);
    BQ.saveTag(image, rangeTags);
end
%%
end
%%
