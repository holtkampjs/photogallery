use photogallery;

drop table if exists department;
drop table if exists employee;
drop table if exists project;
drop table if exists workson;

CREATE TABLE department( 
number varchar(50) NOT NULL PRIMARY KEY, 
name varchar(200) NULL 
); 
 
CREATE TABLE employee ( 
number varchar(100) NOT NULL PRIMARY KEY, 
name varchar(100) NOT NULL, 
salary varchar(20) NOT NULL, 
department_id varchar(20) REFERENCES department (number) 
); 
 
CREATE TABLE project ( 
number varchar(20) NOT NULL PRIMARY KEY, 
name varchar(100) NOT NULL 
); 
 
CREATE TABLE workson ( 
id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, 
employee_id varchar(20) NOT NULL REFERENCES employee (number), 
project_id varchar(20) NOT NULL REFERENCES project (number) 
);
