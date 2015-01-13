#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HBook
import json

id = 288
b = HBook.getBooking(id)
b["state"]=2
sB = json.dumps(b)
HBook.setBooking(id, sB)