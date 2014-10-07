#!/usr/bin/python
# -*- coding: utf-8 -*-

# https://bitbucket.org/robertkoehler/shotwell-export

import sqlite3 as lite
import sys
import os
import shutil

CREATE_DB = """
CREATE TABLE BackingPhotoTable (id INTEGER PRIMARY KEY, filepath TEXT UNIQUE NOT NULL, timestamp INTEGER, filesize INTEGER, width INTEGER, height INTEGER, original_orientation INTEGER, file_format INTEGER, time_created INTEGER );
CREATE TABLE EventTable (id INTEGER PRIMARY KEY, name TEXT, primary_photo_id INTEGER, time_created INTEGER,primary_source_id TEXT);
CREATE TABLE PhotoTable (
    id INTEGER PRIMARY KEY, 
    filename TEXT UNIQUE NOT NULL, 
    width INTEGER, 
    height INTEGER, 
    filesize INTEGER, 
    timestamp INTEGER, 
    exposure_time INTEGER, 
    orientation INTEGER, 
    original_orientation INTEGER, 
    import_id INTEGER, 
    event_id INTEGER, 
    transformations TEXT, 
    md5 TEXT, 
    thumbnail_md5 TEXT, 
    exif_md5 TEXT, 
    time_created INTEGER, 
    flags INTEGER DEFAULT 0, 
    rating INTEGER DEFAULT 0, 
    file_format INTEGER DEFAULT 0, 
    title TEXT, 
    backlinks TEXT, 
    time_reimported INTEGER, 
    editable_id INTEGER DEFAULT -1, 
    metadata_dirty INTEGER DEFAULT 0, 
    developer TEXT, 
    develop_shotwell_id INTEGER DEFAULT -1, 
    develop_camera_id INTEGER DEFAULT -1, 
    develop_embedded_id INTEGER DEFAULT -1);
CREATE TABLE SavedSearchDBTable (id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, operator TEXT NOT NULL);
CREATE TABLE SavedSearchDBTable_Date (id INTEGER PRIMARY KEY, search_id INTEGER NOT NULL, search_type TEXT NOT NULL, context TEXT NOT NULL, date_one INTEGER NOT_NULL, date_two INTEGER NOT_NULL);
CREATE TABLE SavedSearchDBTable_Flagged (id INTEGER PRIMARY KEY, search_id INTEGER NOT NULL, search_type TEXT NOT NULL, flag_state TEXT NOT NULL);
CREATE TABLE SavedSearchDBTable_MediaType (id INTEGER PRIMARY KEY, search_id INTEGER NOT NULL, search_type TEXT NOT NULL, context TEXT NOT NULL, type TEXT NOT_NULL);
CREATE TABLE SavedSearchDBTable_Rating (id INTEGER PRIMARY KEY, search_id INTEGER NOT NULL, search_type TEXT NOT NULL, rating INTEGER NOT_NULL, context TEXT NOT NULL);
CREATE TABLE SavedSearchDBTable_Text (id INTEGER PRIMARY KEY, search_id INTEGER NOT NULL, search_type TEXT NOT NULL, context TEXT NOT NULL, text TEXT);
CREATE TABLE TagTable (id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, photo_id_list TEXT, time_created INTEGER);
CREATE TABLE TombstoneTable (id INTEGER PRIMARY KEY, filepath TEXT NOT NULL, filesize INTEGER, md5 TEXT, time_created INTEGER, reason INTEGER DEFAULT 0 );
CREATE TABLE VersionTable (id INTEGER PRIMARY KEY, schema_version INTEGER, app_version TEXT, user_data TEXT NULL);
CREATE TABLE VideoTable (
    id INTEGER PRIMARY KEY, 
    filename TEXT UNIQUE NOT NULL, 
    width INTEGER, 
    height INTEGER, 
    clip_duration REAL, 
    is_interpretable INTEGER, 
    filesize INTEGER, 
    timestamp INTEGER, 
    exposure_time INTEGER, 
    import_id INTEGER, 
    event_id INTEGER, 
    md5 TEXT, 
    time_created INTEGER, 
    rating INTEGER DEFAULT 0, 
    title TEXT, 
    backlinks TEXT, 
    time_reimported INTEGER, 
    flags INTEGER DEFAULT 0 );
CREATE INDEX PhotoEventIDIndex ON PhotoTable (event_id);
CREATE INDEX SavedSearchDBTable_Date_Index ON SavedSearchDBTable_Date(search_id);
CREATE INDEX SavedSearchDBTable_Flagged_Index ON SavedSearchDBTable_Flagged(search_id);
CREATE INDEX SavedSearchDBTable_MediaType_Index ON SavedSearchDBTable_MediaType(search_id);
CREATE INDEX SavedSearchDBTable_Rating_Index ON SavedSearchDBTable_Rating(search_id);
CREATE INDEX SavedSearchDBTable_Text_Index ON SavedSearchDBTable_Text(search_id);
CREATE INDEX VideoEventIDIndex ON VideoTable (event_id);"""

SELECT_VERISON = "select * from VersionTable"
INSERT_VERSION = "INSERT INTO VersionTable VALUES(?,?,?,?)"

INSERT_PHOTO = "INSERT INTO PhotoTable VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
INSERT_VIDEO = "INSERT INTO VideoTable VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
INSERT_EVENT = "INSERT INTO EventTable VALUES(?,?,?,?,?)"

def SELECT_MEDIA_EVENT_BY_YEAR(table, year):	
	strftime = "strftime('%%s', '%d-01-01')"
	t1 = strftime % year
	t2 = strftime % (year+1)
	tscond = "timestamp between %s and %s" % (t1, t2)
	sql = "SELECT %(mediatable)s.*, EventTable.id, EventTable.name FROM %(mediatable)s " % {'mediatable': table}
	sql += "LEFT JOIN EventTable ON %(mediatable)s.event_id = EventTable.id" % {'mediatable': table}
	sql += " WHERE " + tscond
	return sql

def SELECT_PHOTO_EVENT_BY_YEAR(year):
	sql = SELECT_MEDIA_EVENT_BY_YEAR('PhotoTable', year)
	return sql

def SELECT_VIDEO_EVENT_BY_YEAR(year):
	sql = SELECT_MEDIA_EVENT_BY_YEAR('VideoTable', year)
	print sql
	return sql

def SELECT_EVENTS_BY_IDS(ids):
	sql = "SELECT * FROM EventTable WHERE id IN (%s)" % ",".join(ids)
	return sql
	
datadir = "data/"
thumbsdir = "thumbs/"
thumbs128dir = thumbsdir + "thumbs128/"
thumbs360dir = thumbsdir + "thumbs360/"

srcbasedir = "/home/olivier/.shotwell/"
srcdb = srcbasedir + datadir + "photo.db"

year = 2007
dstbasedir = "/media/Elements/Photos/%d/" % year

if os.path.exists(dstbasedir):
	shutil.rmtree(dstbasedir)
os.makedirs(dstbasedir)
os.makedirs(dstbasedir + datadir)
os.makedirs(dstbasedir + thumbsdir)
os.makedirs(dstbasedir + thumbs128dir)
os.makedirs(dstbasedir + thumbs360dir)

dstcon = lite.connect(dstbasedir + datadir + 'photo.db')
with dstcon:
	dstcur = dstcon.cursor()
	dstcur.executescript(CREATE_DB)

	srccon = lite.connect(srcdb)
	with srccon:
		#
		# Copy VersionTable
		#
		cur = srccon.cursor()
		cur.execute(SELECT_VERISON)
		verdata = cur.fetchone()
		dstcur.execute(INSERT_VERSION, verdata)
		
		eventids = []
		def copy_registers(cur, INSERT, isPhoto):
			i = 0
			for data in cur:
				imgId = data[0]

				# register eventId
				eventid = str(data[-2])
				if eventid not in eventids:
					eventids.append(eventid)

				# create directory
				event = data[-1]
				dstdir = "%s/%s" % (dstbasedir, event)
				if not os.path.exists(dstdir):
					os.makedirs(dstdir)

				# copy file
				srcfile = data[1]
			       	dstfile = "%s/%s" % (dstdir, srcfile.split('/')[-1])
				print "copy image %d - %s - %s" % (imgId, event, srcfile)
				shutil.copy(srcfile, dstdir)
		
				# copy thumbs128 and thumbs360
				format = isPhoto and "thumb%0.16x.jpg" or "video-%0.16x.jpg"
				srcfile = srcbasedir + thumbs128dir + format % imgId
				dstdir = dstbasedir + thumbs128dir
				shutil.copy(srcfile, dstdir)

				srcfile = srcbasedir + thumbs360dir + format % imgId
				dstdir = dstbasedir + thumbs360dir
				shutil.copy(srcfile, dstdir)

				# insert register in dst db
				photodata = data[:-2]
				dstcur.execute(INSERT, photodata)
				i += 1
			return i

		cur.execute(SELECT_PHOTO_EVENT_BY_YEAR(year))
		i = copy_registers(cur, INSERT_PHOTO, True)

		cur.execute(SELECT_VIDEO_EVENT_BY_YEAR(year))
		i += copy_registers(cur, INSERT_VIDEO, False)

		cur.execute(SELECT_EVENTS_BY_IDS(eventids))
		for eventdata in cur:
			dstcur.execute(INSERT_EVENT, eventdata)
			
		print "total", i


# TODO: copy thumbnail
