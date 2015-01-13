#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HCommon
import HValet
import HBook
import json
import twilioPack


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




taskId = 91
newValetId = 3
offlineOldValet = False

booking = HBook.getBooking(taskId)
print str(booking)

oldValetId = booking['valetPersonId']
booking['valetPersonId'] = newValetId

sBooking = json.dumps(booking)
HBook.setBooking(taskId, sBooking)

newValet = HValet.getValet(newValetId)
newValetMobile = newValet["mobile"]

newValet["bookingId"] = taskId
newValet["state"] = HValet.VALET_STATE_BOOKED
newValet["serviceType"] = HBook.SERVICE_VAULT
sValet = json.dumps(newValet)
HValet.setValet(newValetId, sValet)
notifyValetAssignment(newValetMobile)

if oldValetId!=newValetId:
    oldValet = HValet.getValet(oldValetId)
    oldValetMobile = oldValet["mobile"]
    oldValet["bookingId"] = 0
    if offlineOldValet==True:
        oldValet["state"] = 99
    else:
        oldValet["state"] = 0

    oldValet["serviceType"] = HBook.SERVICE_NOW
    sValet = json.dumps(oldValet)

    HValet.setValet(oldValetId, sValet)
    notifyValetCancellation(oldValetMobile)
