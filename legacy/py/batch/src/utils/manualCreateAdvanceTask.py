#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HBook
import json
import HCustomer
import HCommon

j = {}
j['serviceType'] = HBook.SERVICE_ADVANCE
j['taskType'] = 1
j['taskTime'] =  "2014-11-11 14:42"
j['latitude'] =  40.3693014
j['longitude'] =  -74.5533203
j['personId'] =  246
j['carId'] = 149

ret = HBook.scheduleTask(j)
print str(ret)
