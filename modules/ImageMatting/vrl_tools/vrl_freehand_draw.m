function [pts, finish_val] = vrl_freehand_draw(listen_for_press)

%% GCF is the figure handle
%% GCA is the point  handle

global finish_draw;
finish_draw = true;
set(gcf, 'windowbuttondownfcn', {@listen_press});
set(gcf, 'windowbuttonupfcn',   {@listen_release}, 'UserData', []);
    if(listen_for_press)
        set(gcf, 'KeyPressFcn', {@key_press});
    end
set(gcf, 'Interruptible', 'on');
set(gcf, 'BusyAction', 'queue');

set(gca, 'Interruptible', 'on');
set(gca, 'BusyAction', 'cancel');
pts = [];
waitfor(gcf, 'UserData');
finish_val = finish_draw;

    %% Listening for key press
    function listen_press(imagefig, varargins)
        set(gcf, 'windowbuttonmotionfcn', {@listen_points});
    end

    %% For Motion
    function listen_points(imagefig, varargins)
        curr_pt = get(gca, 'CurrentPoint');
        pt = curr_pt(2,1:2);
        pts = [pts; pt];
        N = size(pts, 1);
        if N > 1
            plot([pts(N - 1, 1), pts(N, 1)], [pts(N - 1, 2), pts(N, 2)], 'r', 'LineWidth', 3);
        end
        drawnow;
    end

    %% Listening for release
    function listen_release(imagefig, varargins)
        set(gcf, 'windowbuttonmotionfcn', []);
        set(gcf, 'UserData', 1); 
        %         set(gcf, 'KeyPressFcn', {@printfig});
        %         pause;        
    end
end

function key_press(src,evnt)
    global finish_draw;
        if evnt.Character == 'f'
            finish_draw = false;
            set(gcf, 'UserData', 1); 
        elseif evnt.Character == 'c'
            finish_draw = true;
        else
            error('');
        end
end