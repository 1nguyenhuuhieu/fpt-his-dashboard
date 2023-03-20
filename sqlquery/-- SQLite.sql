-- SQLite
SELECT id, time_created, soluutru,sobenhan, tenbenhnhan, department_name
FROM archived;

DROP TABLE archived


CREATE TABLE `archived` (
	`id` INTEGER PRIMARY KEY  AUTOINCREMENT,
	`time_created` DATETIME,
	`soluutru` VARCHAR,
	`sobenhan` VARCHAR,
	`benhnhan` VARCHAR,
    `khoa` VARCHAR,
    `ngayravien` DATE,
	`is_giveback` BOOLEAN,
	`note` VARCHAR
);

delete from archived
drop table archived