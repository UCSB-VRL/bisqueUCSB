url = 'http://bisque.ece.ucsb.edu/client_service/view?resource=http://bisque.ece.ucsb.edu/data_service/00-VjBR9bmZNwuXC9xFri7xxR';

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% testing basic functionality
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

u = bq.Url(url);
fprintf('toString(): "%s"\n', u.toString());
fprintf('getScheme(): "%s"\n', u.getScheme());
fprintf('getRoot(): "%s"\n', u.getRoot());
fprintf('getPath(): "%s"\n', u.getPath());
fprintf('findQuery(''resource'')): ');
u.findQuery('resource')
fprintf('\n');

u.pushQuery('new_q', 'new_v');
fprintf('pushQuery(): "%s"\n', u.toString());

u.popQuery();
fprintf('popQuery(): "%s"\n', u.toString());

u.pushQuery('new_q', 'new_v');
fprintf('pushQuery(): "%s"\n', u.toString());

u.removeQuery('new_q');
fprintf('removeQuery(): "%s"\n', u.toString());

