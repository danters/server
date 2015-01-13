#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HValet
import json

bookingId = 349
valetId = 20

valet = HValet.getValet(valetId)
valet["bookingId"] = bookingId
valet["state"] = 1
sValet = json.dumps(valet)
HValet.setValet(valetId, sValet)
