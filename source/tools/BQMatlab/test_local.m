%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% tests reading and writing documents from/to files
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

m = bq.Factory.fetch('full_dataset.xml');
m.save('full_dataset_copy.xml');

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% creating new documents
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

outputs = bq.Factory.new('tag', 'outputs');

outputs.addTag('my_number_objects', 123);
outputs.addTag('some_float', 456.78);

rt = outputs.addTag('to_be_removed', 456.78);
s1 = outputs.toString();
rt.remove();
s2 = outputs.toString();

g = outputs.addGobject('my_gobs2', 'my_gobs2');

g.addGobject('point', '1', [1,2,3] );
g.addGobject('point', '2', [4,5,6] );
g.addGobject('point', '3', [7,8,9] );


p = [1,2,3;4,5,6;7,8,9];
g.addGobject('polyline', 'poly-in-z', p );

p = [1,2,-1,3;4,5,-1,6;7,8,-1,9];
g.addGobject('polyline', 'poly-in-t', p );

%% creating tags in another document and attaching them to the current outputs

% attaching a bq.Node
alien = bq.Factory.new('tag', 'alien');
alien.addTag('second_number_objects', 123);
alien.addTag('second_float', 456.78);
outputs.appendChild(alien);

% attaching a DOM Node
alien2 = bq.Factory.new('tag', 'alien2');
alien2.addTag('third_number_objects', 123);
alien2.addTag('third_float', 456.78);
outputs.appendChild(alien2.element);

% attaching an XML string
alien3 = '<tag name="alien3"><tag name="fourth_number_objects" value="123"/><tag name="fourth_float" value="456.78"/></tag>';
outputs.appendChild(alien3);


outputs.save('my_document.xml');


