\set db_name keyimagesdb
\set db_username imexhs
\set db_password imexhs2021
\set quoted_db_password '\'' :db_password '\''

CREATE DATABASE :db_name;

\c :db_name 

CREATE TABLE keyimages
(
    keyimageUID character varying(512),
    patientid character varying(512),
    studyUID character varying(512),
    serieName character varying(512),
    seriesUID character varying(512),
    ismultiframe boolean,
    instanceUID character varying(512),
    slice integer,
    wadoURI character varying(512) NOT NULL,
    timestamp timestamp,
	isFusion boolean,
	backlayer json,
    PRIMARY KEY (keyimageUID)
);

CREATE USER :db_username WITH PASSWORD :quoted_db_password;

GRANT CONNECT ON DATABASE :db_name TO :db_username;

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE "keyimages" TO :db_username;