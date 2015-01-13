#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import json
sys.path.insert(0, "/srv/www/devweb/batch")

import HValet

id=28

v = HValet.getValet(id)
v["codeWord"] = "tesla"
sV = json.dumps(v) 

HValet.setValet(id, sV)
#print str(v)

#{u'authToken': u'2ab803ed-899b-4b90-9583-93854dab806b', u'paymentInfo': u'', u'returnCode': 0, u'carId': 214, u'countryCode': u'US', u'firstName': u'Ben', u'personId': 530, u'lastName': u'Allen', u'mobile': u'6464560576', u'referCode': u'ben7'}