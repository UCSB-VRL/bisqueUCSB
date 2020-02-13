%----------------------------------------------------------------------
% This function generate the spatial domain of the Gabor wavelets
% which are specified by number of scales and orientations and the 
% maximun and minimun center frequency.
% 
%         N : the size of rectangular grid to sample the gabor
%     index : [s,n] specify which gabor filter is selected
%      freq : [Ul,Uh] specify the maximun and minimun center frequency
% partition : [stage,orientation] specify the total number of filters
%      flag : 1 -> remove the dc value of the real part of Gabor
%             0 -> not to remove
%----------------------------------------------------------------------

function [Gr,Gi] = gabor(N,index,freq,partition,flag)

% get parameters

s = index(1);
n = index(2);

Ul = freq(1);
Uh = freq(2);

stage = partition(1);
orientation = partition(2);

% computer ratio a for generating wavelets

base = Uh/Ul;
C = zeros(1,stage);
C(1) = 1;
C(stage) = -base;

P = abs(roots(C));
a = P(1);

% computer best variance of gaussian envelope

u0 = Uh/(a^(stage-s));
Uvar = ((a-1)*u0)/((a+1)*sqrt(2*log(2)));

z = -2*log(2)*Uvar^2/u0;
Vvar = tan(pi/(2*orientation))*(u0+z)/sqrt(2*log(2)-z*z/(Uvar^2));

% generate the spetial domain of gabor wavelets

j = sqrt(-1);

if (rem(N,2) == 0)
    side = N/2-0.5;
else
    side = fix(N/2);
end;

x = -side:1:side;
l = length(x);
y = x';
X = ones(l,1)*x;
Y = y*ones(1,l);

t1 = cos(pi/orientation*(n-1));
t2 = sin(pi/orientation*(n-1));

XX = X*t1+Y*t2;
YY = -X*t2+Y*t1;

Xvar = 1/(2*pi*Uvar);
Yvar = 1/(2*pi*Vvar);

coef = 1/(2*pi*Xvar*Yvar);

Gr = a^(stage-s)*coef*exp(-0.5*((XX.*XX)./(Xvar^2)+(YY.*YY)./(Yvar^2))).*cos(2*pi*u0*XX);
Gi = a^(stage-s)*coef*exp(-0.5*((XX.*XX)./(Xvar^2)+(YY.*YY)./(Yvar^2))).*sin(2*pi*u0*XX);

% remove the real part mean if flag is 1

if (flag == 1)
   m = sum(sum(Gr))/sum(sum(abs(Gr)));
   Gr = Gr-m*abs(Gr);
end;

