CREATE TABLE `post` (
	`post_id` INTEGER PRIMARY KEY,
	`time_created` DATETIME,
	`title` VARCHAR,
	`body` TEXT,
    `username` VARCHAR
);

CREATE TABLE `user` (
	`user_id` INTEGER PRIMARY KEY,
	`user_name` VARCHAR,
	`password` VARCHAR,
    `email` VARCHAR
);

DROP TABLE `post`