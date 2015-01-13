#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HCommon
import HCustomer
import HBook
import HValet
import json

custCred = HCustomer.getCustomerCred(246)
print str(custCred)
HCustomer.clearSingleCustomerCache(246)


bookCount=0
for i in range(0,300):
	booking = HBook.getBookingRaw(i)
	if booking != None:
		bookCount = bookCount + 1
		HBook.clearSingleBookingCache(i)

valetCount=0
for i in range(0,300):
	valet = HValet.getValet(i)
	if valet != None:
		valetCount = valetCount + 1
		HValet.clearSingleValetCache(i)

customerCount=0
for i in range(175,500):
#	customer = HCustomer.getCustomer(i)
#	if customer != None:
#		customerCount=customerCount+1
#		HCustomer.clearSingleCustomerCache(i)
	HCustomer.clearSingleCustomerCache(i)

HCommon.updateProc("call DeleteCityCheckinsAndMore()",())


stuff=HCommon.getCacheValueJson("CUST_CRED_246")
print "stuff=" + str(stuff)


print "Booking  cleared: " + str(bookCount)
print "Valet    cleared: " + str(valetCount)
print "Customer cleared: " + str(customerCount)
