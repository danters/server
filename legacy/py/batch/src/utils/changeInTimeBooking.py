#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HBook
import json

bookingId = 260

booking = HBook.getBooking(bookingId)
booking['inHandoffTime'] = "2014-10-13 15:30:00"
sBooking = json.dumps(booking)
HBook.setBooking(bookingId, sBooking)
