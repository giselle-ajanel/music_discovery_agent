// NOTE: The following script syntax is valid for database version 5.0 and above.

:param {
  // Define the file path root and the individual file names required for loading.
  // https://neo4j.com/docs/operations-manual/current/configuration/file-locations/
  file_path_root: 'file:///', // Change this to the folder your script can access the files at.
  file_0: 'music_connections.csv'
};

// CONSTRAINT creation
// -------------------
//
// Create key and uniqueness constraints for node labels and relationship types. This ensures ID property uniqueness and prevents duplicate entries from being introduced.
//
CREATE CONSTRAINT `ArtistName_Artist_key` IF NOT EXISTS
FOR (n: `Artist`)
REQUIRE (n.`ArtistName`) IS NODE KEY;
CREATE CONSTRAINT `name_Band_key` IF NOT EXISTS
FOR (n: `Band`)
REQUIRE (n.`name`) IS NODE KEY;

:param {
  idsToSkip: [],
  bracketPairs: [["{","}"],["<",">"],["[","]"],["(",")"]]
};

// NODE load
// ---------
//
// Load nodes in batches, one node label at a time. Nodes will be created using a MERGE statement to ensure a node with the same label and ID property remains unique. Pre-existing nodes found by a MERGE statement will have their other properties set to the latest values encountered in a load file.
//
// NOTE: Any nodes with IDs in the 'idsToSkip' list parameter will not be loaded.
LOAD CSV WITH HEADERS FROM ($file_path_root + $file_0) AS row
WITH row
WHERE NOT row.`ArtistName` IN $idsToSkip AND NOT row.`ArtistName` IS NULL
CALL (row) {
  MERGE (n: `Artist` { `ArtistName`: row.`ArtistName` })
  SET n.`ArtistName` = row.`ArtistName`
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM ($file_path_root + $file_0) AS row
WITH row
WHERE NOT row.`BandName` IN $idsToSkip AND NOT row.`BandName` IS NULL
CALL (row) {
  MERGE (n: `Band` { `name`: row.`BandName` })
  SET n.`name` = row.`BandName`
  SET n.`genre` = row.`Genre`
  SET n.`formedYear` = row.`FormedYear`
} IN TRANSACTIONS OF 10000 ROWS;


// RELATIONSHIP load
// -----------------
//
// Load relationships in batches, one relationship type at a time. Relationships are created using a MERGE statement, meaning only one relationship of a given type will ever be created between a pair of nodes.
LOAD CSV WITH HEADERS FROM ($file_path_root + $file_0) AS row
WITH row 
CALL (row) {
  MATCH (source: `Artist` { `ArtistName`: row.`ArtistName` })
  MATCH (target: `Band` { `name`: row.`BandName` })
  MERGE (source)-[r: `MEMBER_OF`]->(target)
  SET r.`Role` = row.`Role`
  SET r.`Connection` = row.`ConnectionType`
} IN TRANSACTIONS OF 10000 ROWS;
