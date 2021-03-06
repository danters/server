#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HCommon
import HValet
import HBook
import json
import twilioPack

def updateValet(j):

    bookingId=j["bookingId"]
    valetId=j["valetId"]

    valet = HValet.getValet(valetId)
    booking = HBook.getBooking(bookingId)
    bookState = booking["state"]

    if bookState == HBook.BOOK_STATE_BOOK_ASSIGNED or \
       bookState == HBook.BOOK_STATE_PARKING_IN_PROGRESS or \
       bookState == HBook.BOOK_STATE_CHECKOUT_IN_PROGRESS or \
       bookState == HBook.BOOK_STATE_CHECKOUT_VALET_ASSIGNED or \
       bookState == HBook.BOOK_STATE_CAR_IN_TRANSIT:

        oldValetId = booking["valetPersonId"]

        if oldValetId==valetId:
            print "Same Valet Selected. valetId: " + str(valetId)
            ret = HCommon.getSuccessReturn()
        else:
            booking["valetPersonId"] = valet["personId"]
            booking["valetAssigned"] = valet
            booking["valet"] = valet
            booking["inValetName"] = valet["firstName"]

            sBook = json.dumps(booking)
            HBook.setBooking(bookingId, sBook)

            valet["bookingId"] = bookingId
            valet["state"] = 1
            sValet = json.dumps(valet)
            print sValet
            HValet.setValet(valetId, sValet)

            valetPhoneNum=str(valet['mobile'])
            notifyValetAssignment(valetPhoneNum)

            oldValet = HValet.getValet(oldValetId)
            oldValet["bookingId"] = 0
            oldValet["state"] = 0
            sValet = json.dumps(oldValet)
            HValet.setValet(oldValetId, sValet)

            oldValetPhoneNum=str(oldValet['mobile'])
            notifyValetCancellation(oldValetPhoneNum)

            HCommon.updateProc("call UpdateCityCheckinAssignValet(%s,%s)", (str(bookingId), str(valetId)))

            ret = HCommon.getSuccessReturn()
    else:
        print "Not Valid booking state. Booking State: " + str(bookState)
        ret = HCommon.getSuccessReturn()

    return ret

def notifyValetAssignment(phoneNum):
    if HCommon.isDev()==True:
        return
    try:
        ret= twilioPack.makeCall(phoneNum)
    except:        
        exc_type, exc_value, exc_traceback = sys.exc_info()
#    		print "Customer Error encountered: " + str(exc_value)

def notifyValetCancellation(phoneNum):
    if HCommon.isDev()==True:
        return
    try:
        ret= twilioPack.cancelBookingCall(phoneNum)
    except:        
        exc_type, exc_value, exc_traceback = sys.exc_info()
#    		print "Customer Error encountered: " + str(exc_value)


