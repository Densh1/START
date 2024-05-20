SELECT 'CREATE DATABASE replaceDB_DATABASE'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'replaceDB_DATABASE')\gexec
CREATE USER replaceDB_REPL_USER WITH REPLICATION ENCRYPTED PASSWORD 'replaceDB_REPL_PASSWORD';
\c replaceDB_DATABASE;
CREATE TABLE emails (
    id INT PRIMARY KEY,
    email VARCHAR(255) NOT NULL
);
CREATE TABLE phone_numbers (
    id INT PRIMARY KEY,
    phone_number VARCHAR(255) NOT NULL
);

INSERT INTO emails (id, email) VALUES (1, 'test1@example.com'), (2, 'test2@example.com');
INSERT INTO phone_numbers (id, phone_number) VALUES (1, '8 (111) 111-11-11'), (2, '8 (222) 222-22-22');

