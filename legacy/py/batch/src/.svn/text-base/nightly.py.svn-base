#!/usr/bin/python
# -*- coding: UTF-8 -*-
import HCommon
import HBook
import HValet
import HCustomer
import json

def makeValetOffline(cityBlockId):
    valets=HCommon.execProcManyRow("call ReadCityBlockValet(%s)",(str(cityBlockId)))

    if valets is None:
        print "No valets"
        return
    
    for lPersonId in valets:
        personId = lPersonId[0]
        print "processing valet " + str(personId)
        
        v = HValet.getValet(personId)
        print str(v)
        if v is not None:
            if v['state']== HValet.VALET_STATE_READY:
                v['state']= HValet.VALET_STATE_NOT_READY
                sValet = json.dumps(v)
                HValet.setValet(personId, sValet)

def cleanCacheOfBookings(forceClean):
    bookings=HCommon.execProcManyRow("call ReadDayLatestCityCheckins()",())

    hasActiveBooking = False;
    for book in bookings:
        bookingId = book[0]
        state = book[1]
        booking = HBook.getBooking(bookingId)
        if booking is not None:
            isActive = False
            if (booking['state'] == HBook.BOOK_STATE_CAR_PARKED or booking['state'] == HBook.BOOK_STATE_CHECKOUT_IN_PROGRESS) and state < HBook.BOOK_STATE_CANCELLED:
                hasActiveBooking = True
                print "booking " + str(bookingId) + " has state " + str(booking["state"])
                isActive = True
            
            if forceClean or isActive==False:
                HBook.clearSingleBookingCache(bookingId)
                customerId = booking["customerPersonId"]
                customer = HCustomer.getCustomer(customerId)
                if customer is not None:
                    customer["bookingId"] = 0
                    sCustomer = json.dumps(customer)
                    HCustomer.setCustomer(customerId, sCustomer)

    return hasActiveBooking

def forceCleanCustomers():
    rows=HCommon.execProcManyRow("call ReadPersons()",())

    for cust in rows:
        customer = HCustomer.getCustomer(cust[0])
        if customer is not None:
            if customer["bookingId"] != 0:
                customer["bookingId"] = 0
                sCustomer = json.dumps(customer)
                HCustomer.setCustomer(customerId, sCustomer)
    
    
cityBlockId = 3

if cleanCacheOfBookings(False) == False:
    makeValetOffline(cityBlockId)
    print "Valets are forced offline"
else:
    print "Unable to offline valets. There are active bookings"
