DROP USER 'Undav'@'localhost';

CREATE USER 'Undav'@'localhost' IDENTIFIED BY '123456788';
GRANT ALL PRIVILEGES ON *.* TO 'Undav'@'localhost';
FLUSH PRIVILEGES;