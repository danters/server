#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HBook
import json
import HCustomer
import HCommon


taskId=25
personId=246
lat =  40.3693014
lng =  -74.5533203
carId= 149

ret = HBook.createBookingFromAdvanceTask(taskId,personId,lat,lng,carId)
print str(ret)
