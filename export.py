#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys
import os
import shutil
import queries
import time
import re

year = 2006

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
        verData = srcCur.fetchone()
        dstCur.execute(queries.INSERT_VERSION, verData)

        eventIds = []

        def makeDirName(event):
            reDate = re.compile("^(\w+ \w+ \d+, \d+)(.*)")
            m = reDate.match(event)
            if m:
                date = m.group(1)
                date = time.strptime(date, "%a %b %d, %Y")
                date = time.strftime("%Y_%m_%d", date)
                dir = date + m.group(2)
            else:
                dir = event
            return dir

        def getDstDir(event, srcFile, expTime):
            if event:
                dstDir = dstBaseDir + makeDirName(event)
            elif srcFile.startswith(srcPhotosDir):
                dir = srcFile[len(srcPhotosDir):]
                dstDir = dstBaseDir + dir
            else:
                date = time.localtime(expTime)
                date = time.strftime("%Y_%m_%d", date)
                dstDir = dstBaseDir + date
            return dstDir

        def copy_registers(cur, INSERT, isPhoto):
            i = 0
            for data in cur:
                imgId = data[0]
                srcFile = data[1]
                expTime = data[isPhoto and 6 or 8]

                # register eventId
                eventId = str(data[-2])
                if eventId != "None" and eventId not in eventIds:
                    print "imgId", imgId, "event", eventId, type(eventId)
                    eventIds.append(eventId)

                # create directory

                # event string is not time-ordered. Try to convert to
                # something time-ordered

                event = data[-1]
                dstDir = getDstDir(event, srcFile, expTime)

                if not os.path.exists(dstDir):
                    os.makedirs(dstDir)

                # copy file
                dstFile = srcFile.split('/')[-1]
                dstFile = "%s/%s" % (dstDir, dstFile)
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
        sql = queries.SELECT_PHOTO_EVENT_BY_YEAR(year)
        srcCur.execute(sql)
        i += copy_registers(srcCur, queries.INSERT_PHOTO, True)

        sql = queries.SELECT_VIDEO_EVENT_BY_YEAR(year)
        srcCur.execute(sql)
        i += copy_registers(srcCur, queries.INSERT_VIDEO, False)

        sql = queries.SELECT_EVENTS_BY_IDS(eventIds)
        print
        print sql
        print
        srcCur.execute(queries.SELECT_EVENTS_BY_IDS(eventIds))
        for eventData in srcCur:
            dstCur.execute(queries.INSERT_EVENT, eventData)

        print "total", i
