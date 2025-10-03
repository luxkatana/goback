-- This file must be run on a MySQL server
DROP TABLE IF EXISTS goback_sites_metadata;
CREATE TABLE IF NOT EXISTS goback_sites_metadata (
    row_id INT NOT NULL AUTO_INCREMENT,
    site_url varchar (100) NOT NULL, -- De site URL
    document_filehash varchar(37) NOT NULL, -- De file hash van het html document dat is opgeslagen in appwrite
    PRIMARY KEY (row_id) -- spreekt wel voor zich, hoop ik :P
);
