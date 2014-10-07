#!/usr/bin/python
# -*- coding: utf-8 -*-

# https://bitbucket.org/robertkoehler/shotwell-export

import sqlite3 as lite
import sys
import os
import shutil
import queries

year = 2007

dataDir = "data/"
thumbsDir = "thumbs/"
thumbs128dir = thumbsDir + "thumbs128/"
thumbs360dir = thumbsDir + "thumbs360/"

srcBaseDir = "/home/olivier/.shotwell/"
srcDb = srcBaseDir + dataDir + "photo.db"

srcPhotosDir = "/media/data/Photos/%d/" % year
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
                srcFile = data[1]

                # register eventId
                eventId = str(data[-2])
                if eventId != "None" and eventId not in eventIds:
                    print "imgId", imgId, "event", eventId, type(eventId)
                    eventIds.append(eventId)

                # create directory

                # event string is not time-ordered. Try to convert to
                # something time-ordered

                # import time
                # date = time.strptime("Fri Sep 1, 2006", "%a %b %d, %Y")
                # time.strftime("%Y_%m_%d", date)

                event = data[-1]
                if event:
                    dstDir = dstBaseDir + event
                elif srcFile.startswith(srcPhotosDir):
                    dstDir = dstBaseDir + srcFile[len(srcPhotosDir):]
                else:
                    dstDir = dstBaseDir + "_misc_"

                if not os.path.exists(dstDir):
                    os.makedirs(dstDir)

                # copy file
                dstFile = "%s/%s" % (dstDir, srcFile.split('/')[-1])
                # print "copy image %d - %s - %s" % (imgId, event, srcFile)
                shutil.copy(srcFile, dstDir)

                # copy thumbs128 and thumbs360
                format = isPhoto and "thumb%0.16x.jpg" or "video-%0.16x.jpg"
                srcFile = srcBaseDir + thumbs128dir + format % imgId
                if os.path.isfile(srcFile):
                    dstDir = dstBaseDir + thumbs128dir
                    shutil.copy(srcFile, dstDir)

                srcFile = srcBaseDir + thumbs360dir + format % imgId
                if os.path.isfile(srcFile):
                    dstDir = dstBaseDir + thumbs360dir
                    shutil.copy(srcFile, dstDir)

                # insert register in dst db
                photoData = data[:-2]
                dstCur.execute(INSERT, photoData)
                i += 1
            return i

        i = 0
        srcCur.execute(queries.SELECT_PHOTO_EVENT_BY_YEAR(year))
        i += copy_registers(srcCur, queries.INSERT_PHOTO, True)

        srcCur.execute(queries.SELECT_VIDEO_EVENT_BY_YEAR(year))
        i += copy_registers(srcCur, queries.INSERT_VIDEO, False)

        sql = queries.SELECT_EVENTS_BY_IDS(eventIds)
        print
        print sql
        print
        srcCur.execute(queries.SELECT_EVENTS_BY_IDS(eventIds))
        for eventData in srcCur:
            dstCur.execute(queries.INSERT_EVENT, eventData)

        print "total", i
