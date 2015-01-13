#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")

import HCustomer
import json

id=530

cred = HCustomer.getCustomerCred(id)
cred["paymentInfo"] = ""

sCred = json.dumps(cred)
HCustomer.setCustomerCred(id, sCred)

print str(cred)