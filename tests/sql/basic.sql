BEGIN TRANSACTION;
DROP TABLE IF EXISTS `articles`;
CREATE TABLE IF NOT EXISTS `articles` (
	`id`	INTEGER NOT NULL,
	`title`	TEXT,
	`body`	TEXT,
	`author_id` INTEGER,
	PRIMARY KEY(`id`),
	FOREIGN KEY (author_id) REFERENCES authors(id)
);

DROP TABLE IF EXISTS `authors`;
CREATE TABLE IF NOT EXISTS `authors` (
	`id`	INTEGER NOT NULL,
	`name`	TEXT,
	PRIMARY KEY(`id`)
);

INSERT INTO 'authors' VALUES (1,'Author 1');
INSERT INTO `articles` VALUES (1,'Article 1','Body 1',1);
INSERT INTO `articles` VALUES (2,'Article 2','Body 2', null);
COMMIT;
