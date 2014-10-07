CREATE TABLE BackingPhotoTable (
	id INTEGER PRIMARY KEY, 					filepath TEXT UNIQUE NOT NULL, 			timestamp INTEGER, 					filesize INTEGER, 						width INTEGER, 
	height INTEGER, 							original_orientation INTEGER, 				file_format INTEGER, 					time_created INTEGER );
CREATE TABLE EventTable (
	id INTEGER PRIMARY KEY, 					name TEXT, 									primary_photo_id INTEGER, 				time_created INTEGER,					primary_source_id TEXT);
CREATE TABLE PhotoTable (
	id INTEGER PRIMARY KEY, 					filename TEXT UNIQUE NOT NULL, 			width INTEGER, 						height INTEGER, 						filesize INTEGER, 					
	timestamp INTEGER, 						exposure_time INTEGER, 					orientation INTEGER, 					original_orientation INTEGER, 			import_id INTEGER,			
	event_id INTEGER,							transformations TEXT,						md5 TEXT, 								thumbnail_md5 TEXT, 					exif_md5 TEXT, 
	time_created INTEGER, 						flags INTEGER DEFAULT 0,					rating INTEGER DEFAULT 0,				file_format INTEGER DEFAULT 0,	 	title TEXT, 								
	backlinks TEXT, 							time_reimported INTEGER, 					editable_id INTEGER DEFAULT -1, 		metadata_dirty INTEGER DEFAULT 0, 	developer TEXT, 					
	develop_shotwell_id INTEGER DEFAULT -1,	develop_camera_id INTEGER DEFAULT -1,		develop_embedded_id INTEGER DEFAULT -1);
	
CREATE TABLE SavedSearchDBTable (id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, operator TEXT NOT NULL);
CREATE TABLE SavedSearchDBTable_Date (id INTEGER PRIMARY KEY, search_id INTEGER NOT NULL, search_type TEXT NOT NULL, context TEXT NOT NULL, date_one INTEGER NOT_NULL, date_two INTEGER NOT_NULL);
CREATE TABLE SavedSearchDBTable_Flagged (id INTEGER PRIMARY KEY, search_id INTEGER NOT NULL, search_type TEXT NOT NULL, flag_state TEXT NOT NULL);
CREATE TABLE SavedSearchDBTable_MediaType (id INTEGER PRIMARY KEY, search_id INTEGER NOT NULL, search_type TEXT NOT NULL, context TEXT NOT NULL, type TEXT NOT_NULL);
CREATE TABLE SavedSearchDBTable_Rating (id INTEGER PRIMARY KEY, search_id INTEGER NOT NULL, search_type TEXT NOT NULL, rating INTEGER NOT_NULL, context TEXT NOT NULL);
CREATE TABLE SavedSearchDBTable_Text (id INTEGER PRIMARY KEY, search_id INTEGER NOT NULL, search_type TEXT NOT NULL, context TEXT NOT NULL, text TEXT);
CREATE TABLE TagTable (id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, photo_id_list TEXT, time_created INTEGER);
CREATE TABLE TombstoneTable (id INTEGER PRIMARY KEY, filepath TEXT NOT NULL, filesize INTEGER, md5 TEXT, time_created INTEGER, reason INTEGER DEFAULT 0 );
CREATE TABLE VersionTable (id INTEGER PRIMARY KEY, schema_version INTEGER, app_version TEXT, user_data TEXT NULL);
CREATE TABLE VideoTable (id INTEGER PRIMARY KEY, filename TEXT UNIQUE NOT NULL, width INTEGER, height INTEGER, clip_duration REAL, is_interpretable INTEGER, filesize INTEGER, timestamp INTEGER, exposure_time INTEGER, import_id INTEGER, event_id INTEGER, md5 TEXT, time_created INTEGER, rating INTEGER DEFAULT 0, title TEXT, backlinks TEXT, time_reimported INTEGER, flags INTEGER DEFAULT 0 );
CREATE INDEX PhotoEventIDIndex ON PhotoTable (event_id);
CREATE INDEX SavedSearchDBTable_Date_Index ON SavedSearchDBTable_Date(search_id);
CREATE INDEX SavedSearchDBTable_Flagged_Index ON SavedSearchDBTable_Flagged(search_id);
CREATE INDEX SavedSearchDBTable_MediaType_Index ON SavedSearchDBTable_MediaType(search_id);
CREATE INDEX SavedSearchDBTable_Rating_Index ON SavedSearchDBTable_Rating(search_id);
CREATE INDEX SavedSearchDBTable_Text_Index ON SavedSearchDBTable_Text(search_id);
CREATE INDEX VideoEventIDIndex ON VideoTable (event_id);
