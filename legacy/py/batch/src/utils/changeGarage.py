#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")

import HCommon
import HBook
import json

garageId = 48
bookingId = 431

b = HBook.getBooking(bookingId)
g = b["garage"]

print "BEFORE -------"
print str(b)

if g["id"] == garageId:
    print "!!! NO CHANGES - SAME GARAGE -------"
else:
    row = HCommon.execProcOneRow("call ReadGarage(%s)",(str(garageId)))
    g['id'] = row[0]
    g['name'] = row[1]
    g['latitude'] = row[2]
    g['longitude'] = row[3]
    g['phone'] = row[4]
    g['address'] = row[5]
    
    HCommon.updateProc("call UpdateCityCheckinGarage(%s,%s)",(str(bookingId),str(garageId)))

    b["garage"] = g
    sB = json.dumps(b)
    HBook.setBooking(bookingId, sB)

print "AFTER -------"
print str(b)