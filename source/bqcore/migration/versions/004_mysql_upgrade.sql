
BEGIN;



ALTER TABLE taggable drop foreign key taggable_ibfk_1;
ALTER TABLE taggable drop column tb_id;

ALTER TABLE taggable drop foreign key taggable_ibfk_3;
ALTER TABLE taggable change column mex mex_id int(11);
ALTER TABLE taggable ADD CONSTRAINT  FOREIGN KEY (mex_id) REFERENCES taggable(id);

ALTER TABLE `values` drop foreign key values_ibfk_2;
ALTER TABLE `values`  change column  parent_id resource_parent_id int(11);
ALTER TABLE `values` ADD CONSTRAINT FOREIGN KEY (resource_parent_id) REFERENCES taggable(id);


alter table vertices drop foreign key vertices_ibfk_1;
alter table vertices  change column  parent_id resource_parent_id int(11);
alter table vertices ADD CONSTRAINT FOREIGN KEY (resource_parent_id) REFERENCES taggable(id);

DROP TABLE service;
DROP TABLE datasets;
DROP TABLE mex;
DROP TABLE modules;
DROP TABLE templates;
DROP TABLE groups;
DROP TABLE users;
DROP TABLE images;
DROP TABLE gobjects;
DROP TABLE tags;
DROP TABLE names;
DROP TABLE file_acl;
DROP TABLE files;

CREATE INDEX resource_document_idx on taggable (document_id);
CREATE INDEX resource_parent_idx on taggable (resource_parent_id);
CREATE INDEX resource_type_idx on taggable (resource_type);

commit;

