#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HBook
import HCustomer
import HValet
import json

id=118
state = HBook.BOOK_STATE_CHECKOUT_VALET_ASSIGNED

v = HBook.getBooking(id)
print "Before"
print str(v)

v["state"] = state
sV = json.dumps(v)
HBook.setBooking(id, sV)
print "After"
print sV

