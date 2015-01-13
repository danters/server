#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HValet
import json

id=45

valet = HValet.getValet(id)
valet["state"] = 0
valet["bookingId"] = 0
sValet = json.dumps(valet)
HValet.setValet(id, sValet)
