#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HValet
import json

id=14

v = HValet.getValet(id)
v["mobile"] = "9177805570"
sV = json.dumps(v)
HValet.setValet(id, sV)