#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HBook
import HCommon
import HCustomer
import HValet
import json

bookingId = 325

booking = HBook.getBooking(bookingId)

row = HCommon.execProcOneRow("call UpdateCityCheckinHandoff(%s,%s,%s)", (str(bookingId),str(HBook.BOOK_STATE_COMPLETED),"0"))

booking['state'] = HBook.BOOK_STATE_COMPLETED
sBooking = json.dumps(booking)
HBook.setBooking(bookingId, sBooking)

customerId = booking["customerPersonId"]
customer = HCustomer.getCustomer(customerId)

customer["state"] = HBook.BOOK_STATE_COMPLETED
customerLocation = json.dumps(customer)
HCustomer.setCustomer(customerId,customerLocation)


valetId = booking["valetPersonId"]
valet = HValet.getValet(valetId)
if valet is not None:
    valet["bookingId"]=0
    valet["state"]=HValet.VALET_STATE_READY
    valet["codeWord"]=""
    sValet = json.dumps(valet)
    HValet.setValet(valetId,sValet)
            
