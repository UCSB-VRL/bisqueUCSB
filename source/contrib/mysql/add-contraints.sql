-- Add constraints to a DB that was Isam

BEGIN;
-- Clean out bad data from before 
delete from tags where id not in (select id from taggable);
delete from `values` where parent_id not in (select id from taggable);
delete from `values` where valobj not in (select id from taggable);
-- Add constraints

ALTER TABLE taggable ADD CONSTRAINT  FOREIGN KEY (tb_id) REFERENCES names(id);
ALTER TABLE taggable ADD CONSTRAINT  FOREIGN KEY (owner_id) REFERENCES taggable(id);
ALTER TABLE taggable ADD CONSTRAINT  FOREIGN KEY (mex) REFERENCES taggable(id);

ALTER TABLE taggable_acl ADD CONSTRAINT  FOREIGN KEY (taggable_id) REFERENCES taggable(id);
ALTER TABLE taggable_acl ADD CONSTRAINT  FOREIGN KEY (user_id) REFERENCES taggable(id);

ALTER TABLE datasets ADD CONSTRAINT FOREIGN KEY (id) REFERENCES taggable(id);

ALTER TABLE gobjects ADD CONSTRAINT FOREIGN KEY (id) REFERENCES taggable(id);
ALTER TABLE gobjects ADD CONSTRAINT  FOREIGN KEY (name_id) REFERENCES names(id);
ALTER TABLE gobjects ADD CONSTRAINT  FOREIGN KEY (type_id) REFERENCES names(id);
ALTER TABLE gobjects ADD CONSTRAINT FOREIGN KEY (parent_id) REFERENCES taggable(id);

ALTER TABLE groups ADD CONSTRAINT FOREIGN KEY (id) REFERENCES taggable(id);
ALTER TABLE images ADD CONSTRAINT FOREIGN KEY (id) REFERENCES taggable(id);
ALTER TABLE mex ADD CONSTRAINT FOREIGN KEY (id) REFERENCES taggable(id);

ALTER TABLE modules ADD CONSTRAINT FOREIGN KEY (id) REFERENCES taggable(id);
ALTER TABLE modules ADD CONSTRAINT  FOREIGN KEY (module_type_id) REFERENCES names(id);

ALTER TABLE service ADD CONSTRAINT FOREIGN KEY (id) REFERENCES taggable(id);

ALTER TABLE tags ADD CONSTRAINT FOREIGN KEY (id) REFERENCES taggable(id);
ALTER TABLE tags ADD CONSTRAINT FOREIGN KEY (parent_id) REFERENCES taggable(id);
ALTER TABLE tags ADD CONSTRAINT FOREIGN KEY (name_id) REFERENCES names(id);
ALTER TABLE tags ADD CONSTRAINT FOREIGN KEY (type_id) REFERENCES names(id);

ALTER TABLE templates ADD CONSTRAINT FOREIGN KEY (id) REFERENCES taggable(id);
ALTER TABLE users ADD CONSTRAINT FOREIGN KEY (id) REFERENCES taggable(id);
ALTER TABLE `values` ADD CONSTRAINT FOREIGN KEY (valobj) REFERENCES taggable(id);
ALTER TABLE `values` ADD CONSTRAINT FOREIGN KEY (parent_id) REFERENCES taggable(id);
ALTER TABLE vertices ADD CONSTRAINT FOREIGN KEY (parent_id) REFERENCES taggable(id);

COMMIT;
