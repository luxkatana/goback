-- This file must be run on a MySQL server
DROP TABLE IF EXISTS goback_sites_metadata;
CREATE TABLE IF NOT EXISTS goback_sites_metadata (
    row_id INT NOT NULL AUTO_INCREMENT,
    site_url varchar (100) NOT NULL, -- De site URL
    document_file_id varchar(37) NOT NULL, -- De file hash van het html document dat is opgeslagen in appwrite (file_id)
    PRIMARY KEY (row_id) -- spreekt wel voor zich, hoop ik :P
);

DROP TABLE IF EXISTS goback_assets_metadata;
CREATE TABLE IF NOT EXISTS goback_assets_metadata (
    id INT NOT NULL AUTO_INCREMENT,
    file_id VARCHAR (38) NOT NULL,
    mimetype VARCHAR (40) DEFAULT "any",
    PRIMARY KEY (id)
);
