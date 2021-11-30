ALTER TABLE projects ADD COLUMN short_name TEXT DEFAULT NULL;
UPDATE projects
SET short_name = 'уголовное наказание за частичную неуплату алиментов'
WHERE
 rowid=3;

UPDATE projects
SET short_name = 'законопроек о введении верхней границы алиментов'
WHERE
 rowid=4;