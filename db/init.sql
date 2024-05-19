CREATE USER repl_user WITH REPLICATION ENCRYPTED PASSWORD 'Qq12345';
SELECT pg_create_physical_replication_slot('replication_slot');

CREATE TABLE hba ( lines text );
COPY hba FROM '/var/lib/postgresql/data/pg_hba.conf';
INSERT INTO hba (lines) VALUES ('host replication all 0.0.0.0/0 md5');
COPY hba TO '/var/lib/postgrsql/data/pg_hba.conf';
SELECT pg_reload_conf();

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

