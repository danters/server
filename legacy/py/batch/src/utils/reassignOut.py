#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HValet
import HBook
import json

id=19
bookingId=278

valet = HValet.getValet(id)
booking = HBook.getBooking(bookingId)
oldValetId = booking["valetPersonId"]
booking["valetPersonId"] = valet["personId"]
booking["valetAssigned"] = valet
booking["valet"] = valet
booking["outValetName"] = valet["firstName"]
booking["outValetId"] = id

sBook = json.dumps(booking)
HBook.setBooking(bookingId, sBook)

valet["bookingId"] = bookingId
valet["state"] = 1
sValet = json.dumps(valet)
HValet.setValet(id, sValet)

oldValet = HValet.getValet(oldValetId)
oldValet["bookingId"] = 0
oldValet["state"] = 0
sValet = json.dumps(oldValet)
HValet.setValet(oldValetId, sValet)
