#!/usr/bin/python
import HCommon
import HCustomer
import HBook
import memcache
import uuid
import json
import sys, traceback

#Valet States
VALET_STATE_NOT_READY = 99;
VALET_STATE_READY = 0;
VALET_STATE_BOOKED = 1;

def getValet(personId):
	key = "VALET_" + str(personId)
        return HCommon.getCacheValueJson(key)

def setValet(personId,value):
	key = "VALET_" + str(personId)
	HCommon.setCacheValue(key, value)

def setValetToken(email, personId, lastName, firstName, mobile,roleCode):
	valet = getValet(personId)
	
	if valet is None or valet["state"] < 1:
		valet = {}
		valet['personId'] = personId
		valet['state'] = VALET_STATE_NOT_READY 
		valet['firstName'] = firstName 
		valet['mobile'] = mobile 
		valet['bookingId'] = 0
		valet['latitude'] = 0
		valet['longitude'] = 0
		valet['codeWord'] = ""
		valetLocation = json.dumps(valet)
		setValet(personId, valetLocation)
        else:
		valet['firstName'] = firstName 
		valet['mobile'] = mobile 
		valetLocation = json.dumps(valet)
		setValet(personId, valetLocation)
            

	key = "VALET_CRED_" + str(personId)
	token = uuid.uuid4()
	
	userData = {}
	userData['returnCode'] = 0 
	userData['personId'] = personId
	userData['lastName'] = lastName
	userData['firstName'] = firstName
	userData['mobile'] = mobile
	userData['roleCode'] = roleCode
	userData['authToken'] = str(token)
	saveData = json.dumps(userData)
	HCommon.setCacheValue(key,saveData)
	
	userData['state'] = valet["state"]
	
	if valet["state"] == VALET_STATE_BOOKED:
            bookingId = valet["bookingId"]
            booking = None
            serviceType = HBook.SERVICE_NOW
            booking = HBook.getBooking(bookingId)
            
            if booking is None:
                valet["bookingId"] = 0
                valet["state"] = VALET_STATE_READY
                valetLocation = json.dumps(valet)
                setValet(personId, valetLocation)
            else:
                serviceType = HBook.getServiceType(bookingId)
                customer = HCustomer.getCustomer(booking["customerPersonId"])
                userData['bookingId'] = valet["bookingId"]
                userData['codeWord'] = valet["codeWord"]
                userData['booking'] = booking
                userData['customer'] = customer
                userData['car'] = HCustomer.getCarInfo(booking["carId"])
                userData["serviceType"] = serviceType
	
	return userData

def getAndValidateValetCred(personId, email, authToken):
	key = "VALET_CRED_" + str(personId)
	userData = HCommon.getCacheValueJson(key)

	if userData is None:
            return None
		
	if authToken != userData["authToken"]:
            return None
		
	valet = getValet(personId)
	
	if valet is None or valet["state"] != VALET_STATE_BOOKED:
            valet = {}
            valet['personId'] = personId
            valet['state'] = VALET_STATE_READY 
            valet['firstName'] = userData["firstName"]
            valet['mobile'] = userData["mobile"]
            valet['bookingId'] = 0
            valet['latitude'] = 0
            valet['longitude'] = 0
            valet['codeWord'] = ""
            valetLocation = json.dumps(valet)
            setValet(personId, valetLocation)

            userData["state"] = VALET_STATE_READY


	if valet["state"] == VALET_STATE_BOOKED:
            bookingId = valet["bookingId"]
            if valet["bookingId"] > 0:
                serviceType = HBook.SERVICE_NOW
                booking = None
                booking = HBook.getBooking(valet["bookingId"])

                if booking is None:
                    valet["bookingId"] = 0
                    valet["state"] = VALET_STATE_READY
                    valetLocation = json.dumps(valet)
                    setValet(personId, valetLocation)
                else:
                    serviceType = HBook.getServiceType(bookingId)
                    customer = HCustomer.getCustomer(booking["customerPersonId"])
                    userData['bookingId'] = valet["bookingId"]
                    userData['codeWord'] = valet["codeWord"]
                    userData['booking'] = booking
                    userData['customer'] = customer
                    userData['state'] = VALET_STATE_BOOKED
                    userData['car'] = HCustomer.getCarInfo(booking["carId"])
                    userData["serviceType"] = serviceType
            else:
                userData['state'] = VALET_STATE_READY
	else:
            userData['state'] = VALET_STATE_READY
	
	return userData
	
		
def getAndRefreshRating(personId):
    row = HCommon.execProcOneRow("call ReadValetRating(%s)",(str(personId)))
    valet = getValet(personId)
    rate = row[0]
    if rate==0:
        rate = 4
    valet['rate'] = rate
    sValet = json.dumps(valet)
    setValet(personId, sValet)
    return valet

def refreshRating(valet):
    personId = valet["personId"]
    row = HCommon.execProcOneRow("call ReadValetRating(%s)",(str(personId)))
    rate = row[0]
    if rate==0:
        rate = 4
    valet['rate'] = rate
    return

def clearAllValetCache():
	mc = HCommon.getMemCache()
	rows=HCommon.execProcManyRow("call ReadValets()",())
	for row in rows:
		key = "VALET_CRED_" + str(row[0])
		useKey = "DEV_" + key if HCommon.isDev() else key
		mc.delete(useKey)

		key = "VALET_" + str(row[0])
		useKey = "DEV_" + key if HCommon.isDev() else key
		mc.delete(useKey)

def clearSingleValetCache(id):
	mc = HCommon.getMemCache()
	key = "VALET_CRED_" + str(id)
	useKey = "DEV_" + key if HCommon.isDev() else key
	mc.delete(useKey)

	key = "VALET_" + str(id)
	useKey = "DEV_" + key if HCommon.isDev() else key
	mc.delete(useKey)

# Below functions are wsgi handlers - direct translation from the previous scripts
# --------------------------------------------------------------------------------
def nearbyFreeValets(j):
    dropoffLatitude=j["dropoffLatitude"]
    dropoffLongitude=j["dropoffLongitude"]

    return HBook.findFreeValetsFromCacheJson(dropoffLatitude, dropoffLongitude)
        
def readUpdateValetLatestLocation(j):
    jValet=j["valet"]

    personId=jValet["personId"]
    valetLatitude=jValet["latitude"]
    valetLongitude=jValet["longitude"]
    valetState=jValet["state"]

    customerPersonId=0
    valet = HBook.updateLocation(False, personId, valetLatitude, valetLongitude)
    booking = None
    
    if valet is None:
        return HCommon.setErrorJson(1, "Unable to set location")

    if valet["state"]==1:
        bookingId = valet["bookingId"]
        if bookingId > 0:
            booking = HBook.getBooking(bookingId)
                
            if booking is not None:
                customerPersonId = booking["customerPersonId"]
            else:
                valet["state"]= 0
        else:
            valet["state"]= 0
            
        if valet["state"]==0:
            sValet = json.dumps(valet)
            setValet(personId, sValet)
            
    valetState = valet["state"]

    ret = HCommon.getSuccessReturn()
    ret["state"] = valetState

    if customerPersonId > 0:
        ret["customer"] = HCustomer.getCustomer(customerPersonId)
        ret["booking"] = booking
    else:
        ret["customer"] = {}
    return ret

def updateRater(j):
    checkinId=j["Checkinid"]
    overallValetRating=j["OverallStars"]
    HCommon.execProcOneRow("call UpdateRater(%s,%s)",(checkinId,overallValetRating))
    return HCommon.getSuccessReturn()

def updateRating(j):
    bookingId=0
    if "checkinId" in j:
        bookingId=j["checkinId"]
    else:
        bookingId=j["bookingId"]
        
    invaletRating=j["checkinValetRating"]
    outvaletRating=j["checkoutValetRating"]
    comment=j["comment"]
    HCommon.execProcOneRow("call UpdateComments(%s,%s,%s,%s)",(bookingId,comment,invaletRating,outvaletRating))
    return HCommon.getSuccessReturn()

def updateValetProfile(j):
    personId=j["personId"]
    firstName=j["firstName"]
    lastName=j["lastName"]
    email=j["email"]
    mobile=j["mobile"]

    rowUpdated = HCommon.execProcOneRow("call UpdateValetProfile(%s,%s,%s,%s,%s)",(str(personId),firstName,lastName,email,mobile))
    ret = HCommon.getSuccessReturn()
    if (rowUpdated > 0):
        ret["isProfileUpdated"] = True
    else:
        ret["returnCode"] = 1
        ret["errorMessage"] = "PersonId not found"
        
    return ret

def updateValetState(j):
    state=j["valetState"]
    valetPersonId=j["valetPersonId"]
    currentLatitude=j["currentLatitude"]
    currentLongitude=j["currentLongitude"]
    valet = getValet(valetPersonId)
    
    if valet["bookingId"] > 0:
        valet['state'] = VALET_STATE_BOOKED
    else:
        valet['state'] = state
        
    valet['latitude'] = currentLatitude
    valet['longitude'] = currentLongitude
    valetLocation = json.dumps(valet)
    setValet(valetPersonId,valetLocation)

    valet['returnCode'] = 0
    return valet

def valetLogin(j):
    email = j["email"]
    password = j["password"]
    row = HCommon.execProcOneRow("call ReadValet(%s,%s)", (email,password))

    if row is None:
        return HCommon.setErrorJson(2,"Email address or password not found")
    else:
        return setValetToken(email, row[0], row[1], row[2], row[3], row[4])
                
def validateValetToken(environ):
    sPersonId = str(environ["Personid"])
    personId = int(sPersonId)
    authToken = environ["Authtoken"]
    email = environ["Email"]

    valet = getAndValidateValetCred(personId, email, authToken)
    if valet is None:
        return HCommon.setErrorJson(1,"Invalid Credentials or Expired Token")
    else:
        return valet

def offlineValet(j):
    personId = j["personId"]
    v = getValet(personId)
    print str(v)
    if v is not None:
        if v['state']== VALET_STATE_READY:
            v['state']= VALET_STATE_NOT_READY
            sValet = json.dumps(v)
            setValet(personId, sValet)
    return HCommon.getSuccessReturn()

def clearValetBooking(j):
    email = j["email"]
    password = j["password"]
    row = HCommon.execProcOneRow("call ReadValet(%s,%s)", (email,password))
    if row is None:
        return HCommon.setErrorJson(2,"Email address or password not found")
    else:
        personId = row[0]
    	valet = getValet(personId)
        if valet is None:
            return HCommon.getSuccessReturn()
        else:
            valet["bookingId"]=0
            valet["state"] = 0
            sValet = json.dumps(valet)
            setValet(personId, sValet)
            return HCommon.getSuccessReturn()
    