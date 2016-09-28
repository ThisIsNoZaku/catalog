DROP DATABASE if exists item_catalog;

CREATE DATABASE item_catalog;

\c item_catalog;

CREATE TABLE items (item_id serial primary key, name text, description text UNIQUE);
CREATE TABLE categories(category_id serial primary key, description text);
CREATE TABLE item_categories(item_id integer references items ON DELETE CASCADE, category_id integer references categories ON DELETE CASCADE);

INSERT INTO categories(description) values('Soccer');
INSERT INTO categories(description) values('Basketball');
INSERT INTO categories(description) values('Baseball');
INSERT INTO categories(description) values('Frisbee');
INSERT INTO categories(description) values('Snowboarding');
INSERT INTO categories(description) values('Rock Climbing');
INSERT INTO categories(description) values('Foosball');
INSERT INTO categories(description) values('Skating');
INSERT INTO categories(description) values('Hockey');

INSERT INTO items(name, description) values('Stick', 'A stick for ice hockey.');
INSERT INTO items(name, description) values('Goggles', 'Goggles to protect the eyes from cold and wind.');
INSERT INTO items(name, description) values('Snowboard', 'Like surfing, but on a mountain.');
INSERT INTO items(name, description) values('Two Shinguards', 'Increasage shin coverage by a factor of 2.');
INSERT INTO items(name, description) values('Shinguard', 'Helps keep your leg from snapping like a twig.');
INSERT INTO items(name, description) values('Frisbee', 'A colorful plastic disc.');
INSERT INTO items(name, description) values('Bat', 'Man');
INSERT INTO items(name, description) values('Jersey', 'Available of your choice of New or English Original.');
INSERT INTO items(name, description) values('Soccer Cleats', 'Known as football shoes among barbarians.');

INSERT INTO item_categories values(1,9);
INSERT INTO item_categories values(2,5);
INSERT INTO item_categories values(3,5);
INSERT INTO item_categories values(4,1);
INSERT INTO item_categories values(5,1);
INSERT INTO item_categories values(6,4);
INSERT INTO item_categories values(7,3);
INSERT INTO item_categories values(8,1);
INSERT INTO item_categories values(9,1);

\c postgres