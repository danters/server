#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import json
import HCustomer
import HCommon

id = 530
mobile = "6464560576"
customer = HCustomer.getCustomer(id)
customer["mobile"] = mobile
sCustomer = json.dumps(customer)
HCustomer.setCustomer(id, sCustomer)
