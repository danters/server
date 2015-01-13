#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HCommon
import HBook
import HCustomer
import HValet
import memcache
import time
import json

f = open("activeBookings.txt","w")
f.write("Content-Type: text/plain;charset=utf-8\n")

rows=HCommon.execProcManyRow("call ReadActiveBookingIds()",())

customerIds = {}
valetIds = {}

f.write("\n=============================\nACTIVE BOOKINGS\n=============================\n")

for row in rows:
    i = row[0]
    booking = HBook.getBooking(i)

    if booking != None:
        customerPersonId = booking["customerPersonId"]
        customerIds[str(customerPersonId)] = customerPersonId
        valetPersonId = booking["valetPersonId"]
        valetIds[str(valetPersonId)] = valetPersonId
        
        
        f.write("BookingId : "+str(i)+" -----\n")
        f.write(json.dumps(booking)+"\n")
        f.write("______________________________________________________________\n")
    else:
        f.write("BookingId : "+str(i)+" not in cached -----\n")
        f.write("______________________________________________________________\n")
                
                
f.write("\n=============================\nACTIVE CUSTOMERS\n=============================\n")
for customerId in customerIds:
    customer = HCustomer.getCustomer(customerId)
    if customer != None:
        f.write("Customer PersonId : "+str(customerId)+" -----\n")
        f.write(json.dumps(customer)+'\n')
        f.write("______________________________________________________________\n")

f.write("\n=============================\nVALETS\n=============================\n")
for i in range(0,300):
    valet = HValet.getValet(i)
    if valet != None:
        f.write("Valet PersonId: "+str(i)+" -----\n")
        f.write(json.dumps(valet)+'\n')
        f.write("______________________________________________________________\n")
