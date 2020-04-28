BEGIN TRANSACTION;
DROP TABLE IF EXISTS `parts`;
CREATE TABLE IF NOT EXISTS `parts` (
	`id`	INTEGER NOT NULL,
	`name`	TEXT,
	`desc`	text,
	PRIMARY KEY(`id`)
);
INSERT INTO `parts` VALUES (1,'part1','some description');
INSERT INTO `parts` VALUES (2,'part2','another description');
DROP TABLE IF EXISTS `flight_controllers`;
CREATE TABLE IF NOT EXISTS `flight_controllers` (
	`id`	INTEGER NOT NULL,
	`parts_id`	INTEGER UNIQUE,
	PRIMARY KEY(`id`)
);
INSERT INTO `flight_controllers` VALUES (1,1);
COMMIT;
