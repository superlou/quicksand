BEGIN TRANSACTION;
DROP TABLE IF EXISTS `articles`;
CREATE TABLE IF NOT EXISTS `articles` (
	`id`	INTEGER NOT NULL,
	`title`	TEXT,
	`body`	TEXT,
	PRIMARY KEY(`id`)
);
INSERT INTO `articles` VALUES (1,'Article 1','Body 1');
INSERT INTO `articles` VALUES (2,'Article 2','Body 2');

DROP TABLE IF EXISTS `authors`;
CREATE TABLE IF NOT EXISTS `authors` (
	`id`	INTEGER NOT NULL,
	`name`	TEXT,
	PRIMARY KEY(`id`)
);
COMMIT;
