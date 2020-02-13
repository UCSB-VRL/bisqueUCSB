

function [a,b,thresh,my_path] = mt_track_init(im,gradients,Ix_start,Iy_start,track_type)

mt_track_config = xml_load('mt_track_config.xml');
%mt_track_config = xml_parseany(fileread('mt_track_config.xml'));

NL = mt_track_config.NL;     % length of normal
d_n = mt_track_config.d_n;
d_p = mt_track_config.d_p;
S = mt_track_config.S;
thresh_s = 2;
Q = S+2;

switch track_type
    case 'trackMotility'
        my_path = mt_trace(im,gradients,Ix_start,Iy_start);
        my_path = smooth_path(my_path);
        [r,my_path] = trellis(im, my_path , d_p , S , NL );
        [a,b,thresh] = get_fg_bg_model(r,S,gradients,thresh_s,[],[]);
    case 'trackinvivo'
        my_path = mt_trace(im,gradients,Ix_start,Iy_start);
        my_path = smooth_path(my_path);
        [r,my_path] = trellis(im, my_path , d_p , S , NL );
        [a,b,thresh] = get_fg_bg_model(r,S,gradients,thresh_s,[],[]);    
    otherwise
        error('Currently either motility and invivo tracking is supported\n');
end




