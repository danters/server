#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")

import HBook
import HCustomer
import HValet

id=49

vault = HBook.getBooking(id)
print "VAULT INFO: " + str(vault)

customerId = vault["customerPersonId"]
customer = HCustomer.getCustomer(customerId)

print "________________"
print "CUSTOMER INFO: " + str(customer)
print "________________"

lat = vault["latitude"]
lng = vault["longitude"]

address = HBook.getAddressFromLatLng(lat,lng)

print "MEETUP LOCATION: " + address

valet = HValet.getValet(vault["valetPersonId"])
print "________________"
print "VALET INFO: " + str(valet)
print "________________"
