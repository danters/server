#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HBook
import HCustomer
import HValet
import json

id=18

v = HBook.getBooking(id)
print str(v)

cId = v["customerPersonId"]
c = HCustomer.getCustomer(cId)
vaId = v["valetPersonId"]
va = HValet.getValet(vaId)

va["bookingId"]=0
va["serviceType"]=HBook.SERVICE_NOW
va["state"] = 99
va["customerPersonId"] = 0

sValet = json.dumps(va)
HValet.setValet(vaId, sValet)

c["bookingId"]=0
sC = json.dumps(c)
HCustomer.setCustomer(cId, sC)

