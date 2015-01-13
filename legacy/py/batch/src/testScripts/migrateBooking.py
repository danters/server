#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HCommon
import HBook
import HCustomer
import HValet
import memcache
import time
import json

id = 510
newId = 5101
booking = HBook.getBooking(id)
booking["id"] = newId
sBooking = json.dumps(booking)
HBook.setBooking(newId, sBooking)
