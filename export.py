#!/usr/bin/python
# -*- coding: utf-8 -*-

# https://bitbucket.org/robertkoehler/shotwell-export

import sqlite3 as lite
import sys
import os
import shutil
import queries

dataDir = "data/"
thumbsDir = "thumbs/"
thumbs128dir = thumbsDir + "thumbs128/"
thumbs360dir = thumbsDir + "thumbs360/"

srcBaseDir = "/home/olivier/.shotwell/"
srcDb = srcBaseDir + dataDir + "photo.db"

year = 2007
dstBaseDir = "/media/Elements/Photos/%d/" % year

if os.path.exists(dstBaseDir):
    shutil.rmtree(dstBaseDir)
os.makedirs(dstBaseDir)
os.makedirs(dstBaseDir + dataDir)
os.makedirs(dstBaseDir + thumbsDir)
os.makedirs(dstBaseDir + thumbs128dir)
os.makedirs(dstBaseDir + thumbs360dir)

dstCon = lite.connect(dstBaseDir + dataDir + 'photo.db')
with dstCon:
    dstCur = dstCon.cursor()
    dstCur.executescript(queries.CREATE_DB)

    srcCon = lite.connect(srcDb)
    with srcCon:
        #
        # Copy VersionTable
        #
        srcCur = srcCon.cursor()
        srcCur.execute(queries.SELECT_VERSION)
        verdata = srcCur.fetchone()
        dstCur.execute(queries.INSERT_VERSION, verdata)

        eventIds = []

        def copy_registers(cur, INSERT, isPhoto):
            i = 0
            for data in cur:
                imgId = data[0]

                # register eventId
                eventId = str(data[-2])
                if eventId not in eventIds:
                    eventIds.append(eventId)

                # create directory
                event = data[-1]
                dstDir = "%s/%s" % (dstBaseDir, event)
                if not os.path.exists(dstDir):
                    os.makedirs(dstDir)

                # copy file
                srcFile = data[1]
                dstFile = "%s/%s" % (dstDir, srcFile.split('/')[-1])
                print "copy image %d - %s - %s" % (imgId, event, srcFile)
                shutil.copy(srcFile, dstDir)

                # copy thumbs128 and thumbs360
                format = isPhoto and "thumb%0.16x.jpg" or "video-%0.16x.jpg"
                srcFile = srcBaseDir + thumbs128dir + format % imgId
                dstDir = dstBaseDir + thumbs128dir
                shutil.copy(srcFile, dstDir)

                srcFile = srcBaseDir + thumbs360dir + format % imgId
                dstDir = dstBaseDir + thumbs360dir
                shutil.copy(srcFile, dstDir)

                # insert register in dst db
                photoData = data[:-2]
                dstCur.execute(INSERT, photoData)
                i += 1
            return i

        srcCur.execute(queries.SELECT_PHOTO_EVENT_BY_YEAR(year))
        i = copy_registers(srcCur, queries.INSERT_PHOTO, True)

        srcCur.execute(queries.SELECT_VIDEO_EVENT_BY_YEAR(year))
        i += copy_registers(srcCur, queries.INSERT_VIDEO, False)

        srcCur.execute(queries.SELECT_EVENTS_BY_IDS(eventIds))
        for eventData in srcCur:
            dstCur.execute(queries.INSERT_EVENT, eventData)

        print "total", i
