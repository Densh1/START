SELECT 'CREATE DATABASE replacedb_database' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'replacedb_database')\gexec
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = 'replacedb_repl_user') THEN
        CREATE USER replacedb_repl_user WITH REPLICATION ENCRYPTED PASSWORD 'replacedb_repl_password'; 
    END IF; 
END $$;

ALTER USER replacepostgres_user WITH PASSWORD 'replacepostgres_password';

\c replaceDB_DATABASE;
CREATE TABLE IF NOT EXISTS emails(
    id INT PRIMARY KEY,
    email VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS phone_numbers(
    id INT PRIMARY KEY,
    phone_number VARCHAR(255) NOT NULL
);

INSERT INTO emails (id, email) VALUES (1, 'test1@example.com'), (2, 'test2@example.com') ON CONFLICT DO NOTHING;
INSERT INTO phone_numbers (id, phone_number) VALUES (1, '8 (111) 111-11-11'), (2, '8 (222) 222-22-22') ON CONFLICT DO NOTHING;