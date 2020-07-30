function [my_path a b thresh] = tracing_module(im,gradients,Ix,Iy);

mt_track_config = xml_load('mt_track_config.xml');
NL = mt_track_config.NL;
d_n = mt_track_config.d_n;
d_p = mt_track_config.d_p;
S = mt_track_config.S;
d_p=1;
thresh_s = 2;
Q = S+2;

my_path = micro_tracing(im,gradients,Ix,Iy);
my_path=smooth_path(my_path);
[r,my_path] = trellis(my_path,d_p,S,NL);
[a,b,thresh] = get_fg_bg_model_train(r,S,gradients,thresh_s);