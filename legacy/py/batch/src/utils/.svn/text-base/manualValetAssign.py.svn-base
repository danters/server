#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")

import HValet
import json

id=14
bookingId = 6

valet = HValet.getValet(id)
valet["state"] = 1
valet["bookingId"] = bookingId
sValet = json.dumps(valet)
HValet.setValet(id,sValet)
print "valet " + str(id) + " is booked to " + str(bookingId)
        