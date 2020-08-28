function ErrorMsg = delAllGobject(client_server,image_url,user,password)
%delAllGobject('http://dough.ece.ucsb.edu','http://dough.ece.ucsb.edu/ds/images/174594','nuclei3d','nuclei3d')
    ErrorMsg = '';
    if(nargin < 4)
        user = 'admin';
        password = 'ucsb2008';
    end
  
    javaaddpath('../../lib/bisque.jar');

    import bisque.*

% Initialize servers and authorize
    BQ = BQMatlab;
    BQ.initServers(client_server,client_server);
    BQ.login(user, password);

    %delete the gobject
    in_image_deep = BQ.loadImage([image_url '?view=deep']);
    image_gobj = in_image_deep.gobjects;
    for i = 0:size(image_gobj)-1
        %if(strcmp(image_gobj.get(i).name, 'AC_Output_SEG_Data'))
            BQ.deleteGObject(image_gobj.get(i));
    end
  
end