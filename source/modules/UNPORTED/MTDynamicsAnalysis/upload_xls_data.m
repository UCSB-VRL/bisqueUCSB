
clear; close all; clc;
image_url = 'http://bodzio.ece.ucsb.edu:8080/ds/images/69';
user = 'admin';
password = 'admin';
init();

%data_dir = '/Users/msargin/mt/life_history/data_and_analysis_table/';
data_dir='./';
data_name = '072507_c2_03_t01.xls';

X = 0.132;
Y = 0.132;

warning off MATLAB:xlsread:Mode
[num, txt, raw]= xlsread([data_dir,data_name]);
warning on MATLAB:xlsread:Mode
N = size(num,1)-1;
length_series = zeros(N,1);

num(:,2)=num(:,2)*X;
num(:,3)=num(:,3)*Y;

for i=1:N
    length_series(i)=sqrt((num(1,2)-num(i+1,2))^2+(num(1,3)-num(i+1,3))^2);
end

time_series = datevec(num(2:end,1));
time_series = sum(time_series.*repmat([0 0 86400 3600 60 1],N,1),2);

time_length_series = [time_series,length_series];

data_str = sprintf('[');
for i = 1:size(time_length_series,1)
    data_str=[data_str,sprintf('%f,%f;',time_length_series(i,1),time_length_series(i,2))];
end
data_str=[data_str,sprintf(']')];

BQAuthorization.setAuthorization(user, password);
tag = BQTag.addTag('data', data_str, 'char');
BQPostTag.postTag(image_url, tag);