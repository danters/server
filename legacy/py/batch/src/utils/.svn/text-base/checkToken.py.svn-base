#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")

import HCustomer

personId=474

customerCred = HCustomer.getCustomerCred(personId)
print str(customerCred)
customer = HCustomer.getCustomer(personId)
print "---------"
print str(customer)
authToken = customerCred["authToken"]
email = ""

ret = HCustomer.getAndValidateCustomerCred(personId,email,authToken)
print str(ret)