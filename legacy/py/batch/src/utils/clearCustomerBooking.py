#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")

import HCustomer
import HBook
import json

id=530

customer = HCustomer.getCustomer(id)
bookingId = customer["bookingId"]
customer["bookingId"] = 0
sCustomer = json.dumps(customer)
HCustomer.setCustomer(id,sCustomer)
print "customer's bookingId set to 0"

serviceType = 1
if "serviceType" in customer:
    serviceType = customer["serviceType"]

if bookingId > 0:
    booking = None
    if serviceType==1:
        HBook.clearSingleBookingCache(bookingId)
        print "Booking cleared"
        