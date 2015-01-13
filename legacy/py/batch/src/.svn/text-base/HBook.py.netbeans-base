#!/usr/bin/python
import HCommon
import HCustomer
import HValet
import json
import urllib
import urllib2
import datetime
import time
import random
import math
import pika
import time
import twilioPack
import sys, traceback
import pytz
import stripe

from datetime import date

#Booking States
BOOK_STATE_BOOKED = 0
BOOK_STATE_BOOK_ASSIGNED = 1
BOOK_STATE_PARKING_IN_PROGRESS = 2
BOOK_STATE_CAR_PARKED = 3
BOOK_STATE_CHECKOUT_IN_PROGRESS = 4
BOOK_STATE_CHECKOUT_VALET_ASSIGNED = 5
BOOK_STATE_CAR_IN_TRANSIT = 6
BOOK_STATE_CAR_IN_CHECKOUT_LOCATION = 7
BOOK_STATE_CANCELLED = 8
BOOK_STATE_COMPLETED = 9
BOOK_STATE_NULL = 99
BOOK_STATE_NOVALETDROPOFF=10

TASK_PARKING = 1
TASK_TO_CUSTOMER = 2

VAULT_CARSTATE_WITHCUSTOMER = 1
VAULT_CARSTATE_INSTORAGE = 2

SERVICE_NOW = 1
SERVICE_ADVANCE = 2
SERVICE_VAULT = 3
SERVICE_AIRPORT = 4

def getBooking(bookingId):
	return HCommon.getCacheValueJson("BOOK_" + str(bookingId))

def getBookingRaw(bookingId):
	return HCommon.getCacheValue("BOOK_" + str(bookingId))

def setBooking(bookingId, bookingText):
	HCommon.setCacheValue("BOOK_" + str(bookingId), bookingText)

def getBookingRaw(bookingId):
	return HCommon.getCacheValue("BOOK_" + str(bookingId))

def setBooking(bookingId, bookingText):
	HCommon.setCacheValue("BOOK_" + str(bookingId), bookingText)

def convertToBookingId(id, serviceType):
    sBookingId = str(id) + str(serviceType)
    return int(sBookingId)

def getServiceType(bookingId):
    sBookingId = str(bookingId)
    sServiceType =  sBookingId[-1]
    return int(sServiceType)

def getDbBookingId(bookingId):
    sBookingId = str(bookingId)
    sBookingId =  sBookingId[:-1]
    return int(sBookingId)

def getFlightStatus(bookId,useCache):
	mc = HCommon.getMemCache()
	if useCache:
		statusData = mc.get(bookId)
		if statusData is not None:
			return statusData

	aInfo=HCommon.getJsonFromProc("call ReadBookingArrivalInfo(%s)", (bookId))
	jaInfo=json.loads("{" + aInfo + "}")

	row=jaInfo["rows"][0]

	appId="9a4ae1c8"
	appKey="4408d5bc10e09499f00d0b51c752b842"

	airlineCode=str(row[0])
	flightNum=str(row[1])
	tDate=str(row[2])
	dDate1=datetime.datetime.strptime(tDate, '%m/%d/%Y').date()

	arrivalDate=str(dDate1.year) + '/' + str(dDate1.month) + '/' + str(dDate1.day)
	url="https://api.flightstats.com/flex/flightstatus/rest/v2/json/flight/status/" + airlineCode + "/" + flightNum + "/arr/" + arrivalDate +"?appId=" + appId + "&appKey=" + appKey
	data=urllib2.urlopen(url).read()
	s=json.loads(data)

	jData=""
	fs =s["flightStatuses"]
	if len(fs) > 0:
		ad = fs[0]["arrivalDate"]
		ar = fs[0]["airportResources"]
		s = fs[0]["status"]
		if "delays" in fs[0]:
			d = json.dumps(fs[0]["delays"])
		else:
			d = '{}'

		jData = '{"arrivalDate": ' + json.dumps(ad) + ', "airportResources":' + json.dumps(ar) + ', "delays":' + d + ', "status":"' + str(s) + '"}'
	if len(fs) == 0:
		jData = '{}'

	return jData

def getNumDays(deptAirDate,arrAirDate):
	dDate1=datetime.datetime.strptime(deptAirDate, '%m/%d/%Y').date()

	dDate2=datetime.datetime.strptime(arrAirDate, '%m/%d/%Y').date()
	dDiff = (dDate2-dDate1).days + 1
	return dDiff

def getTotalAirportPrice(dDiff,priceObj):
	totalCharge = dDiff * priceObj[2]
	return totalCharge

def initiateBookingJson(personId,cityCode,dropoffLongitude,dropoffLatitude,currentLongitude,currentLatitude,priceId,estNumHours,cityBlockId,carId,advanceTaskId):
	garage = findBestGarage(dropoffLatitude, dropoffLongitude)
        if garage is None:
            ret = HCommon.setErrorJson(6, "All garages are full. Unable to initiate a booking")
            ret["booking"] = {}
            ret["errorMessage"] = "All garages are full"
            print "Garages are full"
            return ret

	garageId = garage['id']
	row = HCommon.execProcOneRow("call CreateCityCheckin(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(str(personId),cityCode,str(dropoffLongitude),str(dropoffLatitude),str(currentLongitude),str(currentLatitude),str(priceId),str(estNumHours),str(garageId),str(carId)))
        bookingId = 0
        if advanceTaskId==0:
            bookingId = convertToBookingId(row[0], SERVICE_NOW)
        else:
            bookingId = convertToBookingId(row[0], SERVICE_ADVANCE)


	customer = HCustomer.getCustomer(personId)
	if customer is None:
		customerCred = HCommon.getCacheValueJson("CUST_CRED_" + str(personId))

		customer = {}
		customer['personId'] = personId
		customer['bookingId'] = bookingId
                if advanceTaskId==0:
                    customer['longitude'] = currentLongitude
                    customer['latitude'] = currentLatitude
		customer['firstName'] = customerCred["firstName"]
		customer['mobile'] = customerCred["mobile"]
		customerLocation = json.dumps(customer)
		HCustomer.setCustomer(personId, customerLocation)
		customer = HCustomer.getCustomer(personId)

	customer["bookingId"] = bookingId
	customer["serviceType"] = SERVICE_NOW
        if advanceTaskId==0:
            customer["latitude"] = currentLatitude
            customer["longitude"] = currentLongitude

	customerLocation = json.dumps(customer)
	HCustomer.setCustomer(personId, customerLocation)

	codeWord = getCodeWord()

	booking = {}
	booking['id'] = bookingId
        booking['serviceType'] = SERVICE_NOW
	booking['customerPersonId'] = personId
	booking['customerLatitude'] = currentLatitude
	booking['customerLongitude'] = currentLongitude
	booking['latitude'] = dropoffLatitude
	booking['longitude'] = dropoffLongitude
	booking['valetPersonId'] = 0
	booking['codeWord'] = codeWord
	booking['state'] = BOOK_STATE_BOOKED
	booking['priceId'] = priceId
	booking['estNumHours'] = estNumHours
	booking['priceId'] = priceId
	booking['garage'] = garage
	booking['cityBlockId'] = cityBlockId
	booking['carId'] = carId
        if advanceTaskId>0:
            booking['advanceTaskId'] = advanceTaskId


	bookingText = json.dumps(booking)
	setBooking(bookingId, bookingText)

        msg = {}
        msg["bookingId"] = bookingId
        msg["cityBlockId"] = cityBlockId
        msg["serviceType"] = SERVICE_NOW
        sendToMessageQueue(msg, HCommon.MSG_ASSIGN_DROPOFF)

        ret = HCommon.getSuccessReturn()
        ret["bookingId"] = row[0]
        ret["booking"] = booking
        return ret

def initiateBooking(personId,cityCode,dropoffLongitude,dropoffLatitude,currentLongitude,currentLatitude,priceId,estNumHours,cityBlockId,carId):
        ret = initiateBookingJson(personId,cityCode,dropoffLongitude,dropoffLatitude,currentLongitude,currentLatitude,priceId,estNumHours,cityBlockId,carId,0)
	return json.dumps(ret)

def updateBookingGarage(bookingId,garage):
    garageId = garage["id"]
    HCommon.updateProc("call UpdateCityCheckinGarage(%s,%s)",(str(bookingId),str(garageId)))
    booking = getBooking(bookingId)
    booking['garage'] = garage
    bookingText = json.dumps(booking)
    setBooking(bookingId, bookingText)
    return booking

def sendToMessageQueue(msg, msgType):
        msg["msgType"] = msgType
        sMsg = json.dumps(msg)

        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()
	channel.basic_publish(exchange='',
                      routing_key='bookingQ',
                      body=(sMsg))

def initiateCheckoutJson(bookingId,serviceType,checkoutLatitude,checkoutLongitude,currentLatitude,currentLongitude,expectedTime,checkoutAddress,advanceTaskId):
        booking = getBooking(bookingId)
        if advanceTaskId > 0:
            booking["advanceTaskId"] = advanceTaskId
        else:
            booking["advanceTaskId"] = 0

        personId = booking["customerPersonId"]

	customer = HCustomer.getCustomer(personId)
	customer["latitude"] = currentLatitude
	customer["longitude"] = currentLongitude
	customerLocation = json.dumps(customer)
	HCustomer.setCustomer(personId, customerLocation)


	codeWord = getCodeWord()
	booking['codeWord'] = codeWord
	booking['customerLatitude'] = currentLatitude
	booking['customerLongitude'] = currentLongitude
	booking['latitude'] = checkoutLatitude
	booking['longitude'] = checkoutLongitude
	booking['valetPersonId'] = 0
	booking['valetAssigned'] = {}
	booking['state'] = BOOK_STATE_CHECKOUT_IN_PROGRESS
	booking['expectedTime'] = expectedTime
	booking['checkoutAddress'] = checkoutAddress

        try:
            if serviceType == SERVICE_NOW:
                HCommon.updateProc("call UpdateCityCheckinSetCheckout(%s,%s,%s,%s,%s)",(str(bookingId),str(checkoutLatitude),str(checkoutLongitude),expectedTime,checkoutAddress))

        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            ret = HCommon.setErrorJson(5, "Unable to process request due to error: " + str(exc_value))
            return ret

	bookingText = json.dumps(booking)
        setBooking(bookingId, bookingText)
	ret = {}
	ret["returnCode"] = 0
	ret["bookingId"] = bookingId
	ret["booking"] = booking
	ret["state"] = BOOK_STATE_CHECKOUT_IN_PROGRESS

        msg = {}
        msg["bookingId"] = bookingId
        msg["serviceType"] = SERVICE_NOW
        sendToMessageQueue(msg, HCommon.MSG_ASSIGN_CHECKOUT)

        return ret

def initiateCheckout(bookingId,checkoutLatitude,checkoutLongitude,currentLatitude,currentLongitude,expectedTime,checkoutAddress):
        ret = initiateCheckoutJson(bookingId,checkoutLatitude,checkoutLongitude,currentLatitude,currentLongitude,expectedTime,checkoutAddress,0)

	return json.dumps(ret)

def distance_on_unit_sphere(lat1, long1, lat2, long2):

    # Convert latitude and longitude to
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0

    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians

    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians

    # Compute spherical distance from spherical coordinates.

    # For two locations in spherical coordinates
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) =
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length

    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth
    # in your favorite set of units to get length.
    return arc

def point_in_poly(x,y,poly):

    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside

def getAllCityBlocks():
	cbs = HCommon.getCacheValueJson("CITY_BLOCKS")
	if cbs is None:
		rows=HCommon.execProcManyRow("call ReadCityBlock()",())
		cityBlocks = json.dumps(rows)
		HCommon.setCacheValue("CITY_BLOCKS", cityBlocks)
		return rows
	else:
		return cbs

def readVaultSignupCoverages():
    ret = HCommon.getSuccessReturn()
    HCommon.appendProcResultJson(ret, "vaultSignupCoverages", "call ReadVaultSignupCoverages()",())
    return ret

def getAllVaultCoverage():
	cbs = HCommon.getCacheValueJson("VAULT_COVERAGE")
	if cbs is None:
		rows=HCommon.execProcManyRow("call ReadVaultSignupCoverages()",())
		vaultCoverages = json.dumps(rows)
		HCommon.setCacheValue("VAULT_COVERAGE", vaultCoverages)
		return rows
	else:
		return cbs

def findVaultCoverage(lat, lng):
	point_x = lng
	point_y = lat
	rows = getAllVaultCoverage()
	FoundRow = None
	for row in rows:
		polygon = json.loads(str(row[5]))
		inside = point_in_poly(point_x,point_y,polygon)
		if (inside==True):
			FoundRow = row
			break

	return FoundRow

def findCityBlockFromCache(lat, lng):
	point_x = lng
	point_y = lat
	rows = getAllCityBlocks()
	FoundRow = None
	for row in rows:
		polygon = json.loads(str(row[4]))
		inside = point_in_poly(point_x,point_y,polygon)
		if (inside==True):
			FoundRow = row
			break

	return FoundRow

def findCityBlock(lat, lng):
	point_x = lng
	point_y = lat

	rows=HCommon.execProcManyRow("call ReadCityBlock()",())
	FoundRow = None
	for row in rows:
		polygon = json.loads(str(row[4]))
		inside = point_in_poly(point_x,point_y,polygon)
		if (inside==True):
			FoundRow = row
			break

	return FoundRow

def getCityBlockValets(cityBlockId):
	key = "CITY_BLOCK_VALETS_" + str(cityBlockId)
	cb = HCommon.getCacheValueJson(key)
	if cb is None:
		valets=HCommon.execProcManyRow("call ReadCityBlockValet(%s)",(str(cityBlockId)))
		cbValets = json.dumps(valets)
		HCommon.setCacheValue(key, cbValets)
		return valets
	else:
		return cb

def findFreeValetsFromCacheJson(dropoffLatitude, dropoffLongitude):
        ret = HCommon.getSuccessReturn()
        freeValets = []

	cb = findCityBlockFromCache(dropoffLatitude, dropoffLongitude)

	if cb is not None and len(cb) > 0:
		valets=getCityBlockValets(cb[0])
		for v in valets:
                    for key in v:
                        valetId = key
			loc = HValet.getValet(valetId)
			if loc is not None and loc["state"]==0:
                                freeValets.append(loc)

        ret["valets"] = freeValets
        return ret

def findFreeValetsFromCache(dropoffLatitude, dropoffLongitude):
        ret = findFreeValetsFromCacheJson(dropoffLatitude, dropoffLongitude)
        json.dumps(ret)

def findFreeValets(dropoffLatitude, dropoffLongitude):
	ret = '{"returnCode": 0, "valets": ['
	comma=""

	cb = findCityBlock(dropoffLatitude, dropoffLongitude)
	if cb is not None and len(cb) > 0:
		valets=HCommon.execProcManyRow("call ReadCityBlockValet(%s)",(str(cb[0])))
		for v in valets:
			loc = HValet.getValet(v[0])
			if loc is not None and loc["state"]==0:
				ret += comma + json.dumps(loc)
				comma=","

	ret+= ']}'
	return ret

def convertSQLDateTimeToTimestamp(value):
    return datetime.datetime.fromtimestamp(time.mktime(time.strptime(value, '%Y-%m-%d %H:%M:%S')))

def fromDbDateToEST(utcStr):
    print "time to format: " + utcStr
    gmt = pytz.timezone('UTC')
    eastern = pytz.timezone('US/Eastern')
    utcTime = utcStr + " UTC"

    utcDate = datetime.datetime.strptime(utcTime, '%Y-%m-%d %H:%M:%S UTC')
    dategmt = gmt.localize(utcDate)
    dateeastern = dategmt.astimezone(eastern)
    estTime = str(dateeastern)
    estTime = estTime[:16]
    return estTime

def findBestGarage(dropoffLatitude, dropoffLongitude):
    cb = findCityBlock(dropoffLatitude, dropoffLongitude)
    foundGarage = None
    shortestDistance = 99999999
    if cb is not None and len(cb) > 0:
            garages=HCommon.execProcManyRow("call ReadCityBlockGarages(%s)",(str(cb[0])))
            now = datetime.datetime.utcnow()
            for g in garages:
                    full = False
                    if g[6] is not None:
                        lastFullTime = convertSQLDateTimeToTimestamp(str(g[6]))

                        twoHoursFromFull = lastFullTime + datetime.timedelta(hours=2)

                        if twoHoursFromFull > now:
                            full = True

                    if full == False:
                        distance = distance_on_unit_sphere(dropoffLatitude, dropoffLongitude, g[2], g[3])
                        if shortestDistance > distance:
                                foundGarage = g
                                shortestDistance = distance

    if foundGarage is None:
            return None
    else:
            garageJson = {}
            garageJson['id'] = foundGarage[0]
            garageJson['name'] = foundGarage[1]
            garageJson['latitude'] = foundGarage[2]
            garageJson['longitude'] = foundGarage[3]
            garageJson['phone'] = foundGarage[4]
            garageJson['address'] = foundGarage[5]
            return garageJson

def findBestVaultGarage(cityBlockId,dropoffLatitude, dropoffLongitude):
    foundGarage = None
    shortestDistance = 99999999
    garages = None

    if cityBlockId==0:
        garages=HCommon.execProcManyRow("call ReadAllVaultGarages()",())
    else:
        garages=HCommon.execProcManyRow("call ReadAllVaultCityBlockGarages(%s)",(str(cityBlockId)))

    for g in garages:
        distance = distance_on_unit_sphere(dropoffLatitude, dropoffLongitude, g[2], g[3])
        if shortestDistance > distance:
            foundGarage = g
            shortestDistance = distance


    if foundGarage is None:
        return None
    else:
        return stuffGarageToDict(foundGarage)

def stuffGarageToDict(dbRow):
    g = {}
    g['id'] = dbRow[0]
    g['name'] = dbRow[1]
    g['latitude'] = dbRow[2]
    g['longitude'] = dbRow[3]
    g['phone'] = dbRow[4]
    g['address'] = dbRow[5]
    return g

def getCodeWord_demo():
        return "DEMO2014"

def getCodeWord():
    cnt = 0
    list=['hello','world']
    templatePath = HCommon.getTemplatePath()
    with open(templatePath + 'codewords.txt', 'r') as f:
            for line in f:
                    cnt = cnt + 1
                    list.append(line.rstrip())

    index=random.randrange(2,cnt)
    return list[index]

def assignBestAvailableValet(bookingId,isCheckout,cityBlockId):

	booking = getBooking(bookingId)

        #ensure booking hasn't been assigned to a valet yet
        if isCheckout==True:
            if booking["state"]==BOOK_STATE_CHECKOUT_VALET_ASSIGNED:
                return HValet.getValet(booking["valetPersonId"])
        else:
            if booking["state"]==BOOK_STATE_BOOK_ASSIGNED:
                return HValet.getValet(booking["valetPersonId"])
        
        advanceTaskId = 0
        if "advanceTaskId" in booking:
            advanceTaskId = booking["advanceTaskId"]

	if isCheckout == True:
            cityBlockId = booking["cityBlockId"]

	valets=HCommon.execProcManyRow("call ReadCityBlockValet(%s)",(str(cityBlockId)))
	maxDistance = 9999999999999.99999999
	shortest = maxDistance
	assignedValet = None
	latitude = booking["latitude"]
	longitude = booking["longitude"]

	if isCheckout == True:
            garage = booking["garage"]
            latitude = garage["latitude"]
            longitude = garage["longitude"]

	for v in valets:
            loc = HValet.getValet(v[0])
            if loc is not None and loc["state"]==0:
                    distance = distance_on_unit_sphere(latitude, longitude, loc["latitude"], loc["longitude"])
                    if distance < shortest:
                        shortest = distance
                        assignedValet = loc

	if assignedValet is None:
		return None
	else:
                HValet.refreshRating(assignedValet)
		assignedValet["state"] = HValet.VALET_STATE_BOOKED
		assignedValet["bookingId"] = bookingId
		assignedValet["codeWord"] = booking["codeWord"]
                assignedValet["serviceType"] = booking["serviceType"]

		valetLoc = json.dumps(assignedValet)
		HValet.setValet(assignedValet["personId"], valetLoc)

		customer = HCustomer.getCustomer(booking["customerPersonId"])
		customerText = json.dumps(customer, True)
		HCustomer.setCustomer(booking["customerPersonId"], customerText)

                booking["valetPersonId"] = assignedValet["personId"]

		if isCheckout == True:
                        valetId=assignedValet["personId"]
                        customerId=booking["customerPersonId"]
                        bookingId=assignedValet["bookingId"]
                        sendSupport(valetId,customerId,bookingId,"Return",advanceTaskId)
                        booking['outValetId'] = valetId
                        booking['outValetName'] = assignedValet['firstName']
			booking["state"] = BOOK_STATE_CHECKOUT_VALET_ASSIGNED
			HCommon.updateProc("call UpdateCityCheckinAssignCheckoutValet(%s,%s)", (str(bookingId),assignedValet["personId"]))
		else:
                        valetId=assignedValet["personId"]
                        customerId=booking["customerPersonId"]
                        bookingId=assignedValet["bookingId"]
                        sendSupport(valetId,customerId,bookingId,"Drop Off",advanceTaskId)
                        booking['inValetId'] = assignedValet['personId']
                        booking['inValetName'] = assignedValet['firstName']

			booking["state"] = BOOK_STATE_BOOK_ASSIGNED
			HCommon.updateProc("call UpdateCityCheckinAssignValet(%s,%s)", (str(bookingId),assignedValet["personId"]))

		sBooking = json.dumps(booking)
		setBooking(bookingId, sBooking)

		return assignedValet

def assignBestAvailableVaultValet(bookingId,isCheckout,cityBlockId):

	booking = getBooking(bookingId)

	if isCheckout == True:
            cityBlockId = booking["cityBlockId"]

	valets=HCommon.execProcManyRow("call ReadCityBlockValet(%s)",(str(cityBlockId)))
	maxDistance = 9999999999999.99999999
	shortest = maxDistance
	assignedValet = None
	latitude = booking["latitude"]
	longitude = booking["longitude"]

	if isCheckout == True:
            garage = booking["garage"]
            latitude = garage["latitude"]
            longitude = garage["longitude"]

	for v in valets:
            loc = HValet.getValet(v[0])
            if loc is not None and loc["state"]==0:
                    distance = distance_on_unit_sphere(latitude, longitude, loc["latitude"], loc["longitude"])
                    if distance < shortest:
                        shortest = distance
                        assignedValet = loc

	if assignedValet is None:
		return None
	else:
                HValet.refreshRating(assignedValet)
		assignedValet["state"] = HValet.VALET_STATE_BOOKED
		assignedValet["bookingId"] = bookingId
		assignedValet["codeWord"] = booking["codeWord"]
		assignedValet["serviceType"] = SERVICE_VAULT

		valetLoc = json.dumps(assignedValet)
		HValet.setValet(assignedValet["personId"], valetLoc)

		customer = HCustomer.getCustomer(booking["customerPersonId"])
		customerText = json.dumps(customer, True)
		HCustomer.setCustomer(booking["customerPersonId"], customerText)

                booking["valetPersonId"] = assignedValet["personId"]

		if isCheckout == True:
                        valetId=assignedValet["personId"]
                        customerId=booking["customerPersonId"]
                        bookingId=assignedValet["bookingId"]
                        sendSupport(valetId,customerId,bookingId,"Return",0)
                        booking['outValetName'] = assignedValet['firstName']
                        booking['outValetId'] = assignedValet['personId']
			booking["state"] = BOOK_STATE_CHECKOUT_VALET_ASSIGNED
			HCommon.updateProc("call UpdateCityCheckinAssignCheckoutValet(%s,%s)", (str(bookingId),assignedValet["personId"]))
		else:
                        valetId=assignedValet["personId"]
                        customerId=booking["customerPersonId"]
                        bookingId=assignedValet["bookingId"]
                        sendSupport(valetId,customerId,bookingId,"Drop Off",0)
                        booking['inValetId'] = assignedValet['personId']
                        booking['inValetName'] = assignedValet['firstName']

			booking["state"] = BOOK_STATE_BOOK_ASSIGNED
			HCommon.updateProc("call UpdateCityCheckinAssignValet(%s,%s)", (str(bookingId),assignedValet["personId"]))

		sBooking = json.dumps(booking)
		setBooking(bookingId, sBooking)

		return assignedValet



def sendSupport(valetId,customerId,bookingId,bookingType,advanceTaskId):
    try:
        customerCred = HCustomer.getCustomerCred(customerId)
        customerLast=customerCred["lastName"]
        customerName= customerCred["firstName"]
        customerPh=customerCred["mobile"]

        row=HCommon.execProcOneRow("call ReadBookingInfo(%s,%s)",(str(bookingId),str(valetId)))
        valetName=row[0]
        valetLast=row[1]
        valetPh=row[2]
        checkoutAdd=str(row[3])
        if(checkoutAdd=="None"):
            checkoutAdd="Unavailable(Dropoff)"

        garageName=row[4] + " - " + row[5]

        email='support@valetanywhere.com'
        templatePath = HCommon.getTemplatePath()
        fp = open(templatePath + 'gotBooking.html', 'r')
        msg = fp.read()

        msg = HCommon.replaceVariables(msg, (valetName,valetLast,valetPh,customerName,customerLast,customerPh,str(bookingId),bookingType,garageName,checkoutAdd))
        fp.close()
        if advanceTaskId > 0:
            HCommon.sendEmail(email, "ADVANCE TASK (" + str(advanceTaskId) + ") converted to NOW BOOKING "+" ("+bookingType+") - " + str(bookingId), msg)
        else:
            HCommon.sendEmail(email, "New Booking came in"+" ("+bookingType+") - " + str(bookingId), msg)

    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
	print HCommon.setError(1,str(exc_value))

def vaultEmailToSupport(vault, isNew, firstName, lastName, mobile, garageName, taskTime, address):
    vaultTask = vault["task"]
    sId = str(vaultTask["id"])
    taskType = vaultTask["taskType"]

    estTaskTime = fromDbDateToEST(taskTime + ":00")

    bookingType="Bringing Car to customer"
    if taskType==TASK_PARKING:
        bookingType="Parking Car"

    email='support@valetanywhere.com'
    templatePath = HCommon.getTemplatePath()
    fp = open(templatePath + 'vaultTask.html', 'r')

    msg = fp.read()
    msg = HCommon.replaceVariables(msg, (bookingType,firstName,lastName,mobile,estTaskTime,garageName,address))
    fp.close()

    if isNew == True:
        HCommon.sendEmail(email, "New Monthly Task scheduled "+" ("+bookingType+") - " + sId, msg)
    else:
        HCommon.sendEmail(email, "Monthly Task rescheduled "+" ("+bookingType+") - " + sId, msg)
    return
def advanceEmailToSupport(task, isNew, firstName, lastName, mobile, garageName, taskTime, address):
    sId = str(task["id"])
    taskType = task["taskType"]

    bookingType="Bringing Car to customer"
    if taskType==TASK_PARKING:
        bookingType="Parking Car"

    email='support@valetanywhere.com'
    templatePath = HCommon.getTemplatePath()
    fp = open(templatePath + 'advanceTask.html', 'r')

    msg = fp.read()
    msg = HCommon.replaceVariables(msg, (bookingType,firstName,lastName,mobile,taskTime,garageName,address))

    fp.close()

    if isNew == True:
        HCommon.sendEmail(email, "Advance Task scheduled "+" ("+bookingType+") - " + sId, msg)
    else:
        HCommon.sendEmail(email, "Advance Task rescheduled "+" ("+bookingType+") - " + sId, msg)
    return

def getAddressFromLatLng(lat, lng):
    try:
        googleGeocodeUrl = "https://maps.googleapis.com/maps/api/geocode/json?latlng=" + str(lat) + "," + str(lng) + "&sensor=true_or_false"
        res = urllib.urlopen(googleGeocodeUrl)
        j = json.load(res)
        jAddr = j["results"][0]
        addr = jAddr["formatted_address"]
        addr = addr.encode('ascii', 'xmlcharrefreplace')
        return addr

    except:
        return ""


def handoff(bookingId,serviceType, dbBookingId):
        booking = getBooking(bookingId)
        if serviceType==SERVICE_NOW:
            row = HCommon.execProcOneRow("call UpdateCityCheckinHandoff(%s,%s,%s)", (str(dbBookingId),str(BOOK_STATE_PARKING_IN_PROGRESS),"1"))
            booking['inHandoffTime'] = str(row[0])
        else:
            row = HCommon.execProcOneRow("call UpdateVaultTaskState(%s,%s)", (str(dbBookingId),str(BOOK_STATE_PARKING_IN_PROGRESS)))

	booking['state'] = BOOK_STATE_PARKING_IN_PROGRESS
	sBooking = json.dumps(booking)

        setBooking(bookingId, sBooking)

        msg = {}
        msg["bookingId"] = bookingId
        msg["serviceType"] = serviceType
        sendToMessageQueue(msg, HCommon.MSG_BOOK_STATE_UPDATE)

def carParked(bookingId,serviceType, dbBookingId):
        booking = None
        templatePath = HCommon.getTemplatePath() + 'carParked.html'
        booking = getBooking(bookingId)
        if serviceType==SERVICE_VAULT:
            templatePath = HCommon.getTemplatePath() + 'carParkedVault.html'

	#print str(booking)
	valetId = booking["valetPersonId"]
	customerId = booking["customerPersonId"]
        customerCred = HCustomer.getCustomerCred(customerId)

        carId=booking["carId"]
        carInfo=HCommon.execProcOneRow("call ReadCar(%s)",(str(carId)))
        carMake=carInfo[0]
        carModel=carInfo[1]
        email=customerCred["email"]
        firstName=customerCred["firstName"]
        fp = open(templatePath, 'r')

        msg = fp.read()
        msg = HCommon.replaceVariables(msg, (firstName,carMake,carModel))

        fp.close()
        HCommon.sendEmail(email, "ValetAnywhere Alert - Your Car is Parked!", msg)

        valet = HValet.getValet(valetId)
        if serviceType==SERVICE_NOW:
            HCommon.updateProc("call UpdateCityCheckinStatus(%s,%s)", (str(dbBookingId),str(BOOK_STATE_CAR_PARKED)))
        else:
            HCommon.updateProc("call UpdateVaultTaskState(%s,%s)", (str(dbBookingId),str(BOOK_STATE_CAR_PARKED)))

	valet["bookingId"] = 0
	valet["state"]=HValet.VALET_STATE_READY
	valetLocation = json.dumps(valet)
	HValet.setValet(valetId,valetLocation)

	booking['state'] = BOOK_STATE_CAR_PARKED
	sBooking = json.dumps(booking)
        setBooking(bookingId, sBooking)
        if serviceType==SERVICE_VAULT:
            if "hasRating" in booking and booking["hasRating"]==True:
                customer = HCustomer.getCustomer(customerId)
                customer["bookingId"] = 0
                sCustomer = json.dumps(customer)
                HCustomer.setCustomer(customerId, sCustomer)

        msg = {}
        msg["bookingId"] = bookingId
        msg["serviceType"] = serviceType
        sendToMessageQueue(msg, HCommon.MSG_BOOK_STATE_UPDATE)

def gotCarFromGarage(bookingId,serviceType,dbBookingId):
        if serviceType==SERVICE_NOW:
            HCommon.updateProc("call UpdateCityCheckinStatus(%s,%s)", (str(dbBookingId),str(BOOK_STATE_CAR_IN_TRANSIT)))
        else:
            HCommon.updateProc("call UpdateVaultTaskState(%s,%s)", (str(dbBookingId),str(BOOK_STATE_CAR_IN_TRANSIT)))

        msg = {}
        msg["bookingId"] = bookingId
        msg["serviceType"] = serviceType
        sendToMessageQueue(msg, HCommon.MSG_BOOK_STATE_UPDATE)


def cancelBooking(bookingId,serviceType,dbBookingId):
        booking = getBooking(bookingId)

        if serviceType==SERVICE_NOW:
            HCommon.updateProc("call UpdateCityCheckinStatus(%s,%s)", (str(dbBookingId),str(BOOK_STATE_CANCELLED)))
        else:
            HCommon.updateProc("call UpdateVaultTaskState(%s,%s)", (str(dbBookingId),str(BOOK_STATE_CANCELLED)))
            
        cancelBookingCache(bookingId, booking, serviceType)
        
def cancelBookingCache(bookingId, booking, serviceType):
        valetId = booking["valetPersonId"]
	customerId = booking["customerPersonId"]

	valet = HValet.getValet(valetId)
        valetFirstName = valet["firstName"]
	valetMobile = valet["mobile"]

	customer = HCustomer.getCustomer(customerId)
        customerFirstName = customer["firstName"]
        customerMobile = customer["mobile"]

        valet["bookingId"]=0
	valet["state"]=HValet.VALET_STATE_READY
	valet["codeWord"]=""

	valetLocation = json.dumps(valet)
	HValet.setValet(valetId,valetLocation)

	customer["bookingId"] = 0
	customer["state"] = BOOK_STATE_NULL
	customerLocation = json.dumps(customer)
	HCustomer.setCustomer(customerId,customerLocation)

	booking["state"] = BOOK_STATE_CANCELLED
	bookingText = json.dumps(booking)
        setBooking(bookingId, bookingText)

        msg = {}
        msg["bookingId"] = bookingId
        msg["valetMobile"] = valetMobile
        msg["serviceType"] = serviceType
        sendToMessageQueue(msg, HCommon.MSG_BOOK_STATE_UPDATE)

        emailSupportOnCancel(bookingId, valetFirstName, valetMobile, customerFirstName, customerMobile)

def carReady(bookingId,serviceType,dbBookingId):
        booking = None
        booking = getBooking(bookingId)

        customerMobile = None
        codeWord = None

        if booking is not None:
            customer = HCustomer.getCustomer(booking["customerPersonId"])
            customerMobile = customer["mobile"]
            codeWord = booking["codeWord"]
            carId = booking["carId"]

            carInfo = HCommon.execProcOneRow("call ReadCar(%s)",(str(carId)))
            carName=str(carInfo[0])

        if(customerMobile):
            twilioPack.sendMessageCheckout(customerMobile,carName,codeWord)

        if serviceType==SERVICE_NOW:
            return carReadyAdvanceBooking(bookingId,booking,dbBookingId)
        else:
            return carReadyVaultTask(bookingId,booking,dbBookingId)


def carReadyAdvanceBooking(bookingId,booking,dbBookingId):
        print "carReadyAdvanceBooking: " + str(bookingId) + ", " + str(BOOK_STATE_COMPLETED)
        row = HCommon.execProcOneRow("call UpdateCityCheckinHandoff(%s,%s,%s)", (str(dbBookingId),str(BOOK_STATE_COMPLETED),"0"))

	booking['state'] = BOOK_STATE_CAR_IN_CHECKOUT_LOCATION

	inDateTime=datetime.datetime.strptime(str(row[0]), '%Y-%m-%d %H:%M:%S')
	outDateTime=datetime.datetime.strptime(str(row[1]), '%Y-%m-%d %H:%M:%S')

	inTime = time.mktime(inDateTime.timetuple())
	outTime = time.mktime(outDateTime.timetuple())
	timeDiff = outTime - inTime

	hours = timeDiff / 3600

	booking['timeParked'] = hours
	booking['inHandoffTime'] = str(row[0])
	booking['outHandoffTime'] = str(row[1])
        priceId=str(booking['priceId'])
        hours=round(hours,2)
        sHours=str(hours)

        customerId = booking["customerPersonId"]
        print "customerId=" + str(customerId) + ",hours=" + sHours + ", " + str(1) + "bookingId=" + str(bookingId)
        chargeTotal = HCommon.execProcOneRow("call UpdateComplete(%s,%s,%s,%s,%s)", (str(customerId),sHours,str(1),str(dbBookingId),str(priceId)))
        booking['totalCharge']=chargeTotal[0]
        booking['totalHours']=hours
        booking['credits']=chargeTotal[1]

#        print "Booking after totalCharge"+str(booking)
	sBooking = json.dumps(booking)

        setBooking(bookingId, sBooking)

	customer = HCustomer.getCustomer(customerId)

	customer["state"] = BOOK_STATE_CAR_IN_CHECKOUT_LOCATION
	customerLocation = json.dumps(customer)
	HCustomer.setCustomer(customerId,customerLocation)

        msg = {}
        msg["bookingId"] = bookingId
        msg["serviceType"] = SERVICE_NOW
        sendToMessageQueue(msg, HCommon.MSG_BOOK_STATE_UPDATE)
	return booking

def carReadyVaultTask(vaultTaskId,booking,dbBookingId):
        row = HCommon.execProcOneRow("call UpdateVaultTaskState(%s,%s)", (str(dbBookingId),str(BOOK_STATE_COMPLETED)))
        booking["state"] = BOOK_STATE_CAR_IN_CHECKOUT_LOCATION
        sBooking = json.dumps(booking)
        setBooking(vaultTaskId, sBooking)

        msg = {}
        msg["bookingId"] = vaultTaskId
        msg["serviceType"] = SERVICE_VAULT
        sendToMessageQueue(msg, HCommon.MSG_BOOK_STATE_UPDATE)
        return booking


def emailSupportOnCancel(bookingId, valetFirstName, valetMobile, customerFirstName, customerMobile):
    try:
        email='support@valetanywhere.com'
        templatePath = HCommon.getTemplatePath()
        fp = open(templatePath + 'bookingCancelled.html', 'r')
        msg = fp.read()
        msg = HCommon.replaceVariables(msg, (str(bookingId),valetFirstName,valetMobile,customerFirstName,customerMobile))

        fp.close()
        HCommon.sendEmail(email, "Booking " + str(bookingId) + " cancelled", msg)

        return
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
	print str(exc_value)

def completeBooking(bookingId,serviceType,dbBookingId):
        booking = getBooking(bookingId)
        if serviceType==SERVICE_NOW:
            return completeAdvanceBooking(bookingId,booking,dbBookingId)
        else:
            return completeVaultTask(bookingId,booking,dbBookingId)

def completeAdvanceBooking(bookingId,booking,dbBookingId):
	booking['state'] = BOOK_STATE_COMPLETED
	sBooking = json.dumps(booking)
        setBooking(bookingId, sBooking)

        clearValetFromBooking(booking)

        customerId = booking["customerPersonId"]
	customer = HCustomer.getCustomer(customerId)

	customer["state"] = BOOK_STATE_COMPLETED
	customerLocation = json.dumps(customer)
	HCustomer.setCustomer(customerId,customerLocation)

        if "hasTip" in booking:
            return booking
        else:
            msg = {}
            msg["bookingId"] = bookingId
            msg["serviceType"] = SERVICE_NOW
            sendToMessageQueue(msg, HCommon.MSG_BOOK_STATE_UPDATE)
            return booking

def manualCompleteBooking(j):
        dbBookingId = j["bookingId"]
        customerId = j["personId"]
        checkoutValetId = j["checkoutValetId"]
        checkoutTime = j["checkoutTime"] + ":00"
        tipAmount = j["tipAmount"]
        bookingId = convertToBookingId(dbBookingId, SERVICE_NOW)

        row = HCommon.execProcOneRow("call UpdateCityCheckinHandoff(%s,%s,%s)", (str(dbBookingId),str(BOOK_STATE_COMPLETED),"0"))

        booking = getBooking(bookingId)
        outValet = HValet.getValet(checkoutValetId)

	inDateTime=datetime.datetime.strptime(str(row[0]), '%Y-%m-%d %H:%M:%S')
	outDateTime=datetime.datetime.strptime(checkoutTime, '%Y-%m-%d %H:%M:%S')

	inTime = time.mktime(inDateTime.timetuple())
	outTime = time.mktime(outDateTime.timetuple())
	timeDiff = outTime - inTime

	hours = timeDiff / 3600

        priceId = 8

        hours=round(hours,2)
        sHours=str(hours)

        print "customerId=" + str(customerId) + ",hours=" + sHours + ", " + str(1) + "dbBookingId=" + str(dbBookingId)
        chargeTotal = HCommon.execProcOneRow("call UpdateComplete(%s,%s,%s,%s,%s)", (str(customerId),sHours,str(1),str(dbBookingId),str(priceId)))

        HCommon.execProcOneRow("call UpdateCityCheckinTip(%s,%s)",(str(dbBookingId),str(tipAmount)))

        if booking is not None:
            booking['state'] = BOOK_STATE_COMPLETED
            booking['timeParked'] = hours
            booking['inHandoffTime'] = str(row[0])
            booking['outHandoffTime'] = checkoutTime
            booking['totalCharge']=chargeTotal[0]
            booking['totalHours']=hours
            booking['credits']=chargeTotal[1]
            booking["outValetId"] = checkoutValetId
            booking['outValetName'] = outValet['firstName']
            booking["tipAmount"] = tipAmount
            booking["hasTip"] = True

            sBooking = json.dumps(booking)
            setBooking(bookingId, sBooking)

            clearValetFromBooking(booking)

        customerId = booking["customerPersonId"]
	customer = HCustomer.getCustomer(customerId)

	customer["state"] = BOOK_STATE_COMPLETED
	customerLocation = json.dumps(customer)
	HCustomer.setCustomer(customerId,customerLocation)

	return booking


def completeVaultTask(vaultTaskId,booking,dbBookingId):

        clearValetFromBooking(booking)
        if "hasRating" in booking and booking["hasRating"] == True:
            clearSingleVaultTaskCache(vaultTaskId)

            customerId = booking["customerPersonId"]
            customer = HCustomer.getCustomer(customerId)

            if customer is not None:
                customer["state"] = 99
                customer["bookingId"] = 0
                customerLocation = json.dumps(customer)
                HCustomer.setCustomer(customerId,customerLocation)
        else:
            msg = {}
            msg["bookingId"] = vaultTaskId
            msg["serviceType"] = SERVICE_VAULT
            sendToMessageQueue(msg, HCommon.MSG_BOOK_STATE_UPDATE)
            
        return booking

def clearValetFromBooking(booking):
        valetId = booking["valetPersonId"]
        valet = HValet.getValet(valetId)
        if valet is not None:
            valet["bookingId"]=0
            valet["state"]=HValet.VALET_STATE_READY
            valet["codeWord"]=""
            sValet = json.dumps(valet)
            HValet.setValet(valetId,sValet)

def clearValet(valetId):
        valet = HValet.getValet(valetId)
	valet["bookingId"]=0
	valet["state"]=HValet.VALET_STATE_READY
	valet["codeWord"]=""
        valetLocation = json.dumps(valet)
	HValet.setValet(valetId,valetLocation)

def clearCustomer(customerId):
	customer = HCustomer.getCustomer(customerId)
        customer["bookingId"] = 0
        customer["state"] = BOOK_STATE_COMPLETED
	customerLocation = json.dumps(customer)
	HCustomer.setCustomer(customerId,customerLocation)

def assignCheckoutValet(bookingId,cityBlockId):
	valets=HCommon.execProcManyRow("call ReadCityBlockValet(%s)",(str(cityBlockId)))
	maxDistance = 9999999999999.99999999
	shortest = maxDistance
	assignedValet = None
	booking = getBooking(bookingId)
	latitude = booking["latitude"]
	longitude = booking["longitude"]

	for v in valets:
		loc = HValet.getValet(v[0])
		if loc["state"]==0:
			distance = distance_on_unit_sphere(latitude, longitude, loc["latitude"], loc["longitude"])
			if distance < shortest:
				shortest = distance
				assignedValet = loc

	if assignedValet is None:
		return '{"returnCode": 1, "errorMessage": "No valet available"}'
	else:
		assignedValet["state"] = HValet.VALET_STATE_BOOKED
		assignedValet["bookingId"] = bookingId
		assignedValet["codeWord"] = booking["codeWord"]

		valetLoc = json.dumps(assignedValet)
		HValet.setValet(assignedValet["personId"], valetLoc)

		booking["valetPersonId"] = assignedValet["personId"]
		booking['outValetId'] = assignedValet["personId"]
		sBooking = json.dumps(booking)
		setBooking(bookingId, sBooking)

		HCommon.updateProc("call UpdateCityCheckinAssignCheckoutValet(%s,%s)", (bookingId,assignedValet["personId"]))
		return '{"returnCode": 0, "state": 1,"valetAssigned": ' + valetLoc + ', "booking": ' + sBooking  + ' }'

def updateLocation(isCustomer, personId, latitude, longitude):
	jCacheValue = None
	if isCustomer==True:
		jCacheValue = HCustomer.getCustomer(personId)
	else:
		jCacheValue = HValet.getValet(personId)

        if (jCacheValue is None):
            return None

	jCacheValue["latitude"] = latitude
	jCacheValue["longitude"] = longitude
	location = json.dumps(jCacheValue)

	if isCustomer==True:
		HCustomer.setCustomer(personId, location)
	else:
		HValet.setValet(personId, location)

	return jCacheValue

def clearAllCache():
	mc = HCommon.getMemCache()
	rows=HCommon.execProcManyRow("call ReadCityCheckins()",())
	for row in rows:
		key = "BOOK_" + str(row[0])
		useKey = "DEV_" + key if HCommon.isDev() else key
		mc.delete(useKey)

def clearSingleBookingCache(bookingId):
	mc = HCommon.getMemCache()
	key = "BOOK_" + str(bookingId)
	useKey = "DEV_" + key if HCommon.isDev() else key
	mc.delete(useKey)

def clearSingleVaultTaskCache(bookingId):
	mc = HCommon.getMemCache()
	key = "VAULT_" + str(bookingId)
	useKey = "DEV_" + key if HCommon.isDev() else key
	mc.delete(useKey)

def clearCityBlocksData():
	mc = HCommon.getMemCache()
	key = "CITY_BLOCK_VALETS_1"
	useKey = "DEV_" + key if HCommon.isDev() else key
	mc.delete(useKey)

	key = "CITY_BLOCK_VALETS_2"
	useKey = "DEV_" + key if HCommon.isDev() else key
	mc.delete(useKey)

	key = "CITY_BLOCK_VALETS_3"
	useKey = "DEV_" + key if HCommon.isDev() else key
	mc.delete(useKey)

	key = "CITY_BLOCK_VALETS_4"
	useKey = "DEV_" + key if HCommon.isDev() else key
	mc.delete(useKey)


	key = "CITY_BLOCK_VALETS_5"
	useKey = "DEV_" + key if HCommon.isDev() else key
	mc.delete(useKey)

	key = "CITY_BLOCK_VALETS_6"
	useKey = "DEV_" + key if HCommon.isDev() else key
	mc.delete(useKey)

	key = "CITY_BLOCK_VALETS_7"
	useKey = "DEV_" + key if HCommon.isDev() else key
	mc.delete(useKey)

	key = "CITY_BLOCK_VALETS_8"
	useKey = "DEV_" + key if HCommon.isDev() else key
	mc.delete(useKey)

	key = "CITY_BLOCK_VALETS_9"
	useKey = "DEV_" + key if HCommon.isDev() else key
	mc.delete(useKey)

        key = "CITY_BLOCKS"
	useKey = "DEV_" + key if HCommon.isDev() else key
	mc.delete(useKey)

def clearVaultCoverage():
	mc = HCommon.getMemCache()
	key = "VAULT_COVERAGE"
	useKey = "DEV_" + key if HCommon.isDev() else key
	mc.delete(useKey)

def displayCityBlocksValet():
	mc = HCommon.getMemCache()
	for i in range(1,4):
		key = "CITY_BLOCK_VALETS_" + str(i)
		useKey = "DEV_" + key if HCommon.isDev() else key
		value = mc.get(useKey)
		print str(value)

def getVaultInfo(personId, carId, getTask):
    vault = {}
    row = HCommon.execProcOneRow("call ReadPersonVault(%s,%s)",(str(personId),str(carId)))
    if row is not None:
        startDate = row[2]
        vault["id"] = row[0]
        vault["isActive"] = row[1]
        vault["startDate"] = startDate
        vault["nextBillingDate"] = HCommon.add_month_year(startDate,0,1)
        vault["carState"] = row[3]
        vault["garageId"] = row[4]
        vault["promoCode"] = row[5]
        vault["garageLotNumber"] = row[6]
        vault["carId"] = carId
        vault["homeLatitude"] = row[7]
        vault["homeLongitude"] = row[8]
        vault["homeRadiusMeters"] = row[9]
        vault["carToValetLeadTimeMinutes"] = row[10]
        vault["carToCustomerLeadTimeMinutes"] = row[11]

        price = {}
        price["id"] = row[12]
        price["type"] = row[13]
        price["amount"] = row[14]
        price["description"] = row[15]
        price["additionalRoundTripCharge"] = row[16]
        price["additionalRoundTripSummary"] = row[17]
        price["roundTripSummary"] = row[18]
        vault["price"] = price

        quota = {}
        quota["in"] = row[21]
        quota["out"] = row[22]
        quota["unitCode"] = row[23]
        vault["parkingQuota"] = quota

        usage = {}
        usage["in"] = row[19]
        usage["out"] = row[20]
        vault["currentQuotaUsage"] = usage

        hours = {}
        hours["openTime"] = row[24]
        hours["closeTime"] = row[25]
        hours["utcOffset"] = row[26]
        hours["openDays"] = row[27]
        hours["futureSchedulingLimitDays"] = row[28]
        vault["hoursOfOperation"] = hours
        
        if getTask==True:
            taskRow = HCommon.execProcOneRow("call ReadPersonVaultTask(%s)",(str(personId)))
            task = populateVaultDict(taskRow)
            if task is not None:
                task["developerNote"] = "DON'T USE THIS OBJECT. IT IS DEPRECATED AFTER JANUARY 15, 2015 ON FIRST NATIVE VAULT RELEASE."
                vault["task"] = task

    return vault

def stuffVaultPrice(vault):
    price = {}
    price["monthlyPrice"] = 478
    price["roundTrips"] = 5
    price["extraTripPrice"] = 20
    vault["price"] = price
    return

def populateTaskDict(taskRow, serviceType):
    if taskRow is not None:
        task = {}
        task["serviceType"] = serviceType
        task["id"] = taskRow[0]
        task["taskType"] = taskRow[1]
        task["taskTime"] = str(taskRow[2])
        task["latitude"] = taskRow[3]
        task["longitude"] = taskRow[4]
        task["state"] = taskRow[5]
        task["valetId"] = taskRow[6]
        task["make"] = taskRow[7]
        task["model"] = taskRow[8]
        task["garageId"] = taskRow[9]
        return task
    else:
        return None

def populateVaultDict(taskRow):
    return populateTaskDict(taskRow, SERVICE_VAULT)

def populateAdvanceDict(taskRow):
    return populateTaskDict(taskRow, SERVICE_ADVANCE)

def populateAirportDict(taskRow):
    task = populateTaskDict(taskRow, SERVICE_AIRPORT)
    if task is not None:
        task["departAirlineCode"] = taskRow[10]
        task["DepartFlightNum"] = taskRow[11]
        task["DepartTerminal"] = taskRow[12]
        task["ArriveAirlineCode"] = taskRow[13]
        task["ArriveFlightNum"] = taskRow[14]
        task["ArriveTerminal"] = taskRow[15]
        task["PriceId"] = taskRow[16]
        task["Cost"] = taskRow[17]

# Below functions are wsgi handlers - direct translation from the previous scripts
# --------------------------------------------------------------------------------
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

def manualCreateBookingFromVaultTask(taskType,taskId,personId,lat,lng,valetId,carId,garageId,assignedValet):
    codeWord = getCodeWord()
    cityBlockId = 4
    bookingId = convertToBookingId(taskId, SERVICE_VAULT)

    cb = findCityBlock(lat, lng)
    if cb is not None and len(cb) > 0:
        cityBlockId = cb[0]

    garage = None

    if garageId==0:
        garage = findBestVaultGarage(cityBlockId,lat, lng)
    else:
        foundGarage=HCommon.execProcOneRow("call ReadGarage(%s)",(str(garageId)))
        garage = stuffGarageToDict(foundGarage)

    row = HCommon.execProcOneRow("call ReadPersonVault(%s,%s)",(str(personId),str(carId)))
    if row is not None:
        garage["garageLotNumber"] = row[6]

    address = getAddressFromLatLng(lat, lng)

    booking = {}
    booking['id'] = bookingId
    booking['serviceType'] = SERVICE_VAULT
    booking['customerPersonId'] = personId
    booking['latitude'] = lat
    booking['longitude'] = lng
    booking['valetPersonId'] = valetId
    booking['codeWord'] = codeWord
    booking['cityBlockId'] = cityBlockId
    booking['address'] = address

    bookState = BOOK_STATE_CHECKOUT_VALET_ASSIGNED
    if taskType==TASK_PARKING:
        bookState = BOOK_STATE_BOOK_ASSIGNED

    booking['state'] = bookState

    booking['garage'] = garage
    booking['carId'] = carId
    booking["hasTip"] = False
    booking["hasRating"] = False

    HValet.refreshRating(assignedValet)
    valet = assignedValet
    valet["bookingId"] = bookingId
    valet["state"] = HValet.VALET_STATE_BOOKED
    valet["serviceType"] = SERVICE_VAULT
    valet["codeWord"] = codeWord
    sValet = json.dumps(valet)
    HValet.setValet(valetId, sValet)

    customer = HCustomer.getCustomer(personId)
    customer["bookingId"] = bookingId
    customer["serviceType"] = SERVICE_VAULT
    sCustomer = json.dumps(customer)
    HCustomer.setCustomer(personId, sCustomer)

    updated=HCommon.execProcOneRow("call UpdateVaultTaskAssignment(%s,%s,%s)",(str(taskId), str(BOOK_STATE_BOOK_ASSIGNED), str(valetId)))
    if updated is not None:
        booking["bookingDate"] = updated[1]
    else:
        now = datetime.datetime.utcnow()
        sNow = str(now)
        sNow = sNow[:16]
        booking["bookingDate"] = sNow

    booking["valetAssigned"] = assignedValet
    booking["valet"] = assignedValet
    sBooking = json.dumps(booking)
    setBooking(bookingId, sBooking)

    msg = {}
    msg["bookingId"] = bookingId
    msg["cityBlockId"] = cityBlockId
    msg["serviceType"] = SERVICE_VAULT
    msg["valetMobile"] = valet["mobile"]
    if taskType==TASK_PARKING:
        sendToMessageQueue(msg, HCommon.MSG_ASSIGN_DROPOFF)
    else:
        sendToMessageQueue(msg, HCommon.MSG_ASSIGN_CHECKOUT)

    print "New booking from vault task created: " + str(bookingId)
    return booking

def createBookingFromAdvanceTask(taskId,personId,lat,lng,carId):
    cityCode="NYC"
    estNumHours=0
    cityBlockId = 4
    priceId = 8
    cb = findCityBlock(lat, lng)
    if cb is not None and len(cb) > 0:
        cityBlockId = cb[0]
    ret =  initiateBookingJson(personId,cityCode,lng,lat,lng,lat,priceId,estNumHours,cityBlockId,carId,taskId)
    bookingId = ret["bookingId"]
    updated=HCommon.execProcOneRow("call UpdateAdvanceTaskConverted(%s,%s)",(str(taskId),str(bookingId)))
    return ret

def manualUpdateBookingFromVaultTask(taskId,valetId):

    bookingId = convertToBookingId(taskId, SERVICE_VAULT)
    valet = {}
    valet["bookingId"] = bookingId
    valet["valetId"] = valetId

    print "In manualUpdateBokingFromVaultTask: valet:" + str(valet)

    updateValet(valet)

    booking = None
    booking = getBooking(bookingId)
    
    updated=HCommon.execProcOneRow("call UpdateVaultTaskAssignment(%s,%s,%s)",(str(taskId), str(BOOK_STATE_BOOK_ASSIGNED), str(valetId)))
    if updated is not None:
        booking["bookingDate"] = updated[1]
    else:
        now = datetime.datetime.utcnow()
        sNow = str(now)
        sNow = sNow[:16]
        booking["bookingDate"] = sNow

    sBooking = json.dumps(booking)
    setBooking(bookingId, sBooking)

    print "Valet updated for booking from vault task: " + str(bookingId) + str(valetId)
    return booking

def bookingStateDisplay(j):
    	email = j["email"]
	password = j["password"]
	row = HCommon.execProcOneRow("call ReadValet(%s,%s)", (email,password))

	if row is None:
		return HCommon.setErrorJson(2,"Email address or password not found")
	else:
		return HValet.setValetToken(email, str(row[0]), row[1], row[2], row[3], row[4])

def clearBookingFromCache(j):
    dbBookingId = j["bookingId"]
    bookingId = convertToBookingId(dbBookingId, SERVICE_NOW)
    clearSingleBookingCache(bookingId)
    return HCommon.getSuccessReturn()

def garageFull(j):
    garageId = j["garageId"]
    bookingId = j["bookingId"]
    lat = j["lat"]
    lng = j["lng"]

    HCommon.updateProc("call UpdateGarageFull(%s)",(str(garageId)))

    garage = findBestGarage(lat, lng)

    ret = HCommon.getSuccessReturn()

    if garage is None:
        ret["booking"] = {}
        ret["errorMessage"] = "All garages are full"
    else:
        booking = updateBookingGarage(bookingId,garage)
        ret["booking"] = booking

    return ret

def initiateCheckout(j):
    bookingId=j["bookingId"]
    serviceType=SERVICE_NOW
    if "serviceType" in j:
        serviceType = j["serviceType"]

    if "pickupLocation" in j:
        #v2 specs
        expectedTime=j["pickupTime"]
        pickupLocation=j["pickupLocation"]
        customer=j["customer"]

        checkoutPlace=""
        if "address" in pickupLocation:
            checkoutPlace=pickupLocation["address"]
            checkoutPlace = checkoutPlace.encode('ascii', 'xmlcharrefreplace')

        checkoutLatitude=pickupLocation["latitude"]
        checkoutLongitude=pickupLocation["longitude"]
        currentLongitude=customer["latitude"]
        currentLatitude=customer["longitude"]
        return initiateCheckoutJson(bookingId,serviceType,checkoutLatitude,checkoutLongitude,currentLatitude,currentLongitude,expectedTime,checkoutPlace,0)
    else:
        #v1.0 specs
        expectedTime=j["expectedTime"]
        checkoutPlace=j["checkoutPlace"]
        checkoutLatitude=j["checkoutLatitude"]
        checkoutLongitude=j["checkoutLongitude"]
        currentLongitude=j["currentLongitude"]
        currentLatitude=j["currentLatitude"]
        return initiateCheckoutJson(bookingId,serviceType,checkoutLatitude,checkoutLongitude,currentLatitude,currentLongitude,expectedTime,checkoutPlace,0)

def initiateDropOff(j):
    personId=j["personId"]
    cityCode=j["cityCode"]

    dropoffLatitude=j["dropoffLatitude"]
    dropoffLongitude=j["dropoffLongitude"]

    currentLongitude=j["currentLongitude"]
    currentLatitude=j["currentLatitude"]

    priceId=j["priceId"]
    estNumHours=j["estNumHours"]
    cityBlockId = j["cityBlockId"]
    carId = j["carId"]
    if carId < 1:
        return HCommon.setErrorJson(11, "carId must have a valid value")
    else:
        return initiateBookingJson(personId,cityCode,dropoffLongitude,dropoffLatitude,currentLongitude,currentLatitude,priceId,estNumHours,cityBlockId,carId,0)

def applyCoupon(j):
    personId=j['personId']
    couponCode=j['promoCode']
    row = HCommon.execProcOneRow("call UpdateCoupon(%s,%s)",(str(personId),str(couponCode)))    #print "CouponDetails"+str(couponDetails)
    ret =HCommon.getSuccessReturn()

    res = row[0]

    if res==1:
        ret["returnCode"] = 200
        ret["errorMessage"] = "The promotion code has already been applied to your account"
    elif res==2:
        ret["returnCode"] = 201
        ret["errorMessage"] = "Invalid Promotion Code"
    else:
        return HCustomer.readCredits(j)

    return ret

def readBookingState(j):
    bookingId=j["bookingId"]
    booking = getBooking(bookingId)

    state = booking["state"]
    ret = HCommon.getSuccessReturn()
    ret['state'] = state
    ret['booking'] = booking

    if state==BOOK_STATE_BOOK_ASSIGNED or state==BOOK_STATE_PARKING_IN_PROGRESS:
        valet = HValet.getValet(booking["valetPersonId"])
        ret['valetAssigned'] = valet

    elif state==BOOK_STATE_CAR_PARKED:
        ret['garage'] = booking["garage"]

    elif state==BOOK_STATE_CHECKOUT_VALET_ASSIGNED or state==BOOK_STATE_CAR_IN_TRANSIT or state==BOOK_STATE_CAR_IN_CHECKOUT_LOCATION:
        valet = HValet.getValet(booking["valetPersonId"])
        ret['valetAssigned'] = valet

    return ret


def readCityBlock(j):
    lng = j["longitude"]
    lat = j["latitude"]

    ret = HCommon.getSuccessReturn()
    row = findCityBlock(lat, lng)

    if row is None:
        ret["returnCode"] = 1
        ret["errorMessage"] = "Dropoff location is not yet served by ValetAnywhere"
    else:
        ret["cityBlockId"] = row[0]
        ret["priceId"] = row[5]

    return ret

def sendCheckoutMessage(j):
    if HCommon.isDev()==True:
        return HCommon.getSuccessReturn()
    customerId = j["customerId"]
    carId=j["carId"]
    codeWord=j["codeWord"]
    customerId=str(customerId)
    customerInfo = HCommon.execProcOneRow("call ReadPersonbyId(%s)",(customerId))
    customerMobile=str(customerInfo[2])
    carId=str(carId)
    carInfo = HCommon.execProcOneRow("call ReadCar(%s)",(carId))
    carName=str(carInfo[0])
    if(customerMobile):
        twilioPack.sendMessageCheckout(customerMobile,carName,codeWord)

    return HCommon.getSuccessReturn()

def sendDropOffMessage(j):
    if HCommon.isDev()==True:
        return
    customerId = j["customerId"]
    valetName=j["valetName"]
    codeWord=j["codeWord"]
    customerId=str(customerId)
    customerInfo = HCommon.execProcOneRow("call ReadPersonbyId(%s)",(customerId))
    customerMobile=str(customerInfo[2])
    if(customerMobile):
        twilioPack.sendMessageDropOff(customerMobile,valetName,codeWord)

    return HCommon.getSuccessReturn()


def updateBookingState(j):
#    print "Booking Completed!"
    bookingId=j["bookingId"]
    serviceType = getServiceType(bookingId)
    dbBookingId=getDbBookingId(bookingId)

    state=j["bookingState"]
    booking = None
    booking = getBooking(bookingId)

    if booking is None:
        ret = HCommon.getSuccessReturn()
        ret['state'] = BOOK_STATE_NULL
        ret['booking'] = {}
        return ret

    booking['state'] = state
    sBooking = json.dumps(booking)
    setBooking(bookingId, sBooking)

    if state==BOOK_STATE_PARKING_IN_PROGRESS:
        handoff(bookingId,serviceType,dbBookingId)

    elif state==BOOK_STATE_CAR_PARKED:
        carParked(bookingId,serviceType,dbBookingId)

    elif state==BOOK_STATE_CAR_IN_TRANSIT:
        gotCarFromGarage(bookingId,serviceType,dbBookingId)

    elif state==BOOK_STATE_CAR_IN_CHECKOUT_LOCATION:
        carReady(bookingId,serviceType,dbBookingId)

    elif state==BOOK_STATE_CANCELLED:
        cancelBooking(bookingId,serviceType,dbBookingId)

    elif state==BOOK_STATE_COMPLETED:
        booking = completeBooking(bookingId,serviceType,dbBookingId)

    else:
        if serviceType==SERVICE_NOW:
            HCommon.updateProc("call UpdateCityCheckinStatus(%s,%s)", (dbBookingId,str(state)))

    ret = HCommon.getSuccessReturn()
    ret['state'] = state
    ret['booking'] = booking
    return ret

def viewPersonBookings(j):
    personId=j["personId"]
    ret = HCommon.getSuccessReturn()
    HCommon.appendProcResultJson(ret, "bookings", "call ReadPersonCityCheckins(%s)",(str(personId)))
    HCommon.appendProcResultJson(ret, "monthlyTransactions", "call ReadPersonVaultTransactions(%s)",(str(personId)))

    #bookings=HCommon.execProcManyRowToArrays("call ReadPersonCityCheckins(%s)",(str(personId)))

    #ret["bookings"] = bookings
    return ret

def InvalidScheduleTimeMessage(serviceType, taskTime):
    #Christmas Block Period
    #sBlockStartTime = "2014-12-24 22:00"
    #sBlockEndTime = "2014-12-26 12:00"

    #New Year Block Period
    sBlockStartTime = "2014-12-31 22:00"
    sBlockEndTime = "2015-01-02 12:00"

    #Test Block Period
    #sBlockStartTime = "2014-12-22 21:00"
    #sBlockEndTime = "2014-12-23 12:00"

    blockStartTime = HCommon.dbDateToEST(sBlockStartTime)
    blockEndTime = HCommon.dbDateToEST(sBlockEndTime)
    estTaskTime = HCommon.dbDateToEST(taskTime)

    now = datetime.datetime.utcnow()
    sNow = str(now)
    sNow = sNow[:16]
    estNow = HCommon.dbDateToEST(sNow)

    #New Year Block Period
    sBlockStartTime = "2014-12-31 22:00"
    sBlockEndTime = "2015-01-02 12:00"
    blockStartTime = HCommon.dbDateToEST(sBlockStartTime)
    blockEndTime = HCommon.dbDateToEST(sBlockEndTime)

    if estNow >= blockStartTime and  estNow <= blockEndTime:
        if estTaskTime >= blockStartTime and  estTaskTime <= blockEndTime:
            return "We are close during New Year's eve and New Year's day. We will open again 7AM on January 2. For emergencies, please call our support hotline at (646) 481-2212."

    taskTime_plus_60 = estTaskTime + datetime.timedelta(minutes = 60)

    if taskTime_plus_60 < estNow:
        return "You scheduled a time beyond the allowed lead time. If you are currently not in New York timezone, please adjust the schedule time based on your local timezone to correspond to New York timezone."

    return None

def scheduleTask(j):
    serviceType = j["serviceType"]
    taskType = j["taskType"]
    taskTime = j["taskTime"]

    invalidTimeMsg = InvalidScheduleTimeMessage(serviceType, taskTime)
    if invalidTimeMsg is not None:
        return HCommon.setErrorJson(210, invalidTimeMsg)


    lat = j["latitude"]
    lng = j["longitude"]
    personId = j["personId"]
    carId = j["carId"]
    partnerAbbr = ""
    if "partner" in j:
        partnerAbbr = j["partner"]

    garageId=0
    garageDesc = ""
    garageName = ""
    garage = None
    hasGarage = False
    if serviceType==SERVICE_ADVANCE:
        garage = findBestGarage(lat,lng)
    elif serviceType==SERVICE_VAULT:
        row=HCommon.execProcOneRow("call ReadPersonVaultGarage(%s,%s)",(str(personId), str(carId)))
        if row is not None:
            garageId = row[0]
            garageName = row[1]
            garageDesc = row[2]
            if garageId > 0:
                hasGarage = True

        if hasGarage==True:
            cityBlockId = 0
            cb = findCityBlock(lat, lng)
            if cb is not None and len(cb) > 0:
                cityBlockId = cb[0]
            garage = findBestVaultGarage(cityBlockId,lat,lng)

    if garage is not None:
        garageId = garage["id"]
        garageName = garage["name"]
        garageDesc = garage["address"]

    address = getAddressFromLatLng(lat, lng)

    customerCred = HCustomer.getCustomerCred(personId)
    email = customerCred["email"]
    firstName = customerCred["firstName"]
    lastName = customerCred["lastName"]
    mobile = customerCred["mobile"]

    oldFormat = 0
    if "oldFormat" in j:
        oldFormat = 1

    if serviceType==SERVICE_ADVANCE:
        return createAdvanceTask(partnerAbbr,personId,taskType,lat,lng,taskTime,carId,garageId,garageDesc,address,garageName,email,firstName,lastName,mobile)
    elif serviceType==SERVICE_VAULT:
        return createVaultTask(partnerAbbr,personId,taskType,lat,lng,taskTime,carId,garageId,garageDesc,address,garageName,email,firstName,lastName,mobile, oldFormat)

    return {}

def rescheduleTask(j):
    serviceType = j["serviceType"]
    vaultTaskId = j["vaultTaskId"]
    taskTime = j["taskTime"]
    lat = j["latitude"]
    lng = j["longitude"]

    ret = HCommon.getSuccessReturn()

    if serviceType==SERVICE_ADVANCE:
        #do advance update task here
        return None
    elif serviceType==SERVICE_VAULT:
        row=HCommon.execProcOneRow("call UpdateVaultTask(%s,%s,%s,%s)",(str(vaultTaskId), str(lat), str(lng), taskTime))
        personId = row[15]
        carId = row[16]
        taskType = row[1]

        vault = getVaultInfo(personId,carId,False)
        vault["task"] = populateVaultDict(row)
        ret["vault"] = vault
        address = getAddressFromLatLng(lat, lng)
        garageDesc = row[14] + " - " + row[17]

        taskDateEST = HCommon.dbDateToEST_String(taskTime)
        taskDate = taskDateEST[:10]
        estTaskTime = taskDateEST[11:]
        estTaskTime = taskDate + " " + HCommon.toStdTime(estTaskTime)
        customerCred = HCustomer.getCustomerCred(personId)
        email = customerCred["email"]
        firstName = customerCred["firstName"]

        emailTaskToCustomer(False, email, taskType,firstName,estTaskTime,address)

        vaultEmailToSupport(vault, False, row[11], row[12], row[13], garageDesc, taskTime, address)

    return ret

def cancelTask(j):
    taskId = j["taskId"]
    row=HCommon.execProcOneRow("call ReadTask(%s)",(str(taskId)))

    if row is None:
        return HCommon.setErrorJson(203, "Unable to find the scheduled task you're trying to cancel.")
    serviceType = row[0]
    firstName = row[3]
    email = row[4]
    taskTime = row[2]

    taskDateEST = HCommon.dbDateToEST_String(taskTime)
    taskDate = taskDateEST[:10]
    taskTime = taskDateEST[11:]
    taskTime = taskDate + " " + HCommon.toStdTime(taskTime)


    updated=HCommon.execProcOneRow("call UpdateTaskCancelled(%s)",(str(taskId)))
    ret = HCommon.getSuccessReturn()

    templatePath = HCommon.getTemplatePath() + 'vaultCancelCustomerNotification.html'
    if serviceType==SERVICE_ADVANCE:
        templatePath = HCommon.getTemplatePath() + 'advanceCancelCustomerNotification.html'

    fp = open(templatePath, 'r')
    msg = fp.read()
    fp.close()

    msg = HCommon.replaceVariables(msg, (firstName,str(taskTime)))
    #email="dante@valetanywhere.com"
    HCommon.sendEmail(email, "Scheduled Valet Parking Cancelled", msg)

    
    bookingId = convertToBookingId(taskId, SERVICE_VAULT)
    booking = getBooking(bookingId)
    if booking is not None:
        cancelBookingCache(bookingId, booking, SERVICE_VAULT)
    
    return ret

def createAdvanceTask(partnerAbbr,personId,taskType,lat,lng,taskTime,carId,garageId,garageDesc,address,garageName,email,firstName,lastName,mobile):
    row=HCommon.execProcOneRow("call CreateAdvanceTask(%s,%s,%s,%s,%s,%s,%s)",(str(personId), str(taskType), taskTime, str(lat), str(lng),str(carId),str(garageId)))
    print "Advance Task Row Created: " + str(row)

    make = row[7]
    model = row[8]
    isExisting = row[10]

    taskDateEST = HCommon.dbDateToEST_String(taskTime)
    taskDate = taskDateEST[:10]
    taskTime = taskDateEST[11:]
    taskTime = taskDate + " " + HCommon.toStdTime(taskTime)

    templatePath = HCommon.getTemplatePath() + 'advanceCustomerNotification.html'

    msg = None
    fp = open(templatePath, 'r')
    msg = fp.read()
    fp.close()

    taskDesc = "meet you to park your " + make + " " + model
    if taskType == 2:
        taskDesc = "bring your " + make + " " + model + " to you"

    msg = HCommon.replaceVariables(msg, (firstName,taskDesc,address,taskTime))

    if isExisting==1:
        HCommon.sendEmail(email, "ValetAnywhere Rescheduled Valet Parking", msg)
    else:
        HCommon.sendEmail(email, "ValetAnywhere Scheduled Valet Parking", msg)

    ret = HCommon.getSuccessReturn()
    task = populateAdvanceDict(row)
    ret["task"] =task

    garageDesc = garageName + " - " + str(garageDesc)
    advanceEmailToSupport(task, True, firstName, lastName, mobile, garageDesc, taskTime,address)
    return ret

def createVaultTask(partnerAbbr,personId,taskType,lat,lng,taskTime,carId,garageId,garageDesc,address,garageName,email,firstName,lastName,mobile, oldFormat):
    row=HCommon.execProcOneRow("call CreateVaultTask(%s,%s,%s,%s,%s,%s,%s)",(str(personId), str(taskType), str(lat), str(lng), taskTime,str(carId),str(garageId)))
    print "Vault Task Row Created: " + str(row)


    taskDateEST = HCommon.dbDateToEST_String(taskTime)
    taskDate = taskDateEST[:10]
    estTaskTime = taskDateEST[11:]
    estTaskTime = taskDate + " " + HCommon.toStdTime(estTaskTime)
    customerCred = HCustomer.getCustomerCred(personId)
    email = customerCred["email"]
    sAddress = address.encode('ascii', 'xmlcharrefreplace')

    if row[15]==1:

        monthlyPrice = "478.00"
        billDay = taskTime[8:10]
        customerName = row[11]


        templatePath = HCommon.getTemplatePath() + 'signup' + partnerAbbr + 'VaultWelcome.html'

        fp = open(templatePath, 'r')
        msg = fp.read()

        if len(partnerAbbr) > 0:
            msg = HCommon.replaceVariables(msg, (customerName,str(address),str(estTaskTime)))
        else:
            msg = HCommon.replaceVariables(msg, (customerName,str(address),str(estTaskTime),str(billDay)))

        fp.close()
        HCommon.sendEmail(email, "ValetAnywhere Monthly First Parking", msg)
    else:
        emailTaskToCustomer(True, email, taskType,firstName,estTaskTime,sAddress)

    ret = HCommon.getSuccessReturn()
    vault = getVaultInfo(personId,carId,False)
    vault["task"] = populateVaultDict(row)
    if oldFormat==1:
        ret["vault"] = vault
    else:
        ret["task"] = populateVaultDict(row)

    garageDesc = garageName + " - " + str(garageDesc)
    vaultEmailToSupport(vault, True, firstName,lastName,mobile, garageDesc, taskTime,address)
    return ret


def emailTaskToCustomer(newSchedule, email, taskType,firstName,estTaskTime,sAddress):
    taskDesc = "meet you to park your car"
    sched = "rescheduled"
    if newSchedule == True:
        sched = "scheduled"

    subject = "ValetAnywhere Monthly - Car dropoff " + sched
    if taskType == 2:
        taskDesc = "bring your car to you"
        subject = "ValetAnywhere Monthly - Car return " + sched


    templatePath = HCommon.getTemplatePath() + 'vaultCustomerNotification.html'

    fp = open(templatePath, 'r')
    msg = fp.read()
    sAddress = sAddress.encode('ascii', 'xmlcharrefreplace')

    msg = HCommon.replaceVariables(msg, (firstName,estTaskTime,taskDesc,sAddress))
    fp.close()
    HCommon.sendEmail(email, subject, msg)
    return

def updateValet(j):

    print "updateValet"

    bookingId=j["bookingId"]
    valetId=j["valetId"]

    valet = HValet.getValet(valetId)
    booking = getBooking(bookingId)
    bookState = booking["state"]

    if bookState == BOOK_STATE_BOOK_ASSIGNED or \
       bookState == BOOK_STATE_PARKING_IN_PROGRESS or \
       bookState == BOOK_STATE_CHECKOUT_IN_PROGRESS or \
       bookState == BOOK_STATE_CHECKOUT_VALET_ASSIGNED or \
       bookState == BOOK_STATE_CAR_IN_TRANSIT:

        oldValetId = booking["valetPersonId"]

        if oldValetId==valetId:
            print "Same Valet Selected. valetId: " + str(valetId)
            valet["bookingId"] = bookingId
            valet["state"] = 1
            sValet = json.dumps(valet)
            print sValet
            HValet.setValet(valetId, sValet)
            ret = HCommon.getSuccessReturn()
        else:
            booking["valetPersonId"] = valet["personId"]
            booking["valetAssigned"] = valet
            booking["valet"] = valet
            booking["inValetName"] = valet["firstName"]

            sBook = json.dumps(booking)
            setBooking(bookingId, sBook)

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



def populatePersonTasks(ret, personId):
    rows=HCommon.execProcManyRow("call ReadPersonAllActiveTasks(%s)",(str(personId)))
    tasks = []
    for row in rows:
        task = {}
        task["id"] = row[0]
        task["serviceType"] = row[1]
        task["taskType"] = row[2]
        task["taskTime"] = row[3]
        task["latitude"] = row[4]
        task["longitude"] = row[5]
        task["carId"] = row[6]
        task["make"] = row[7]
        task["model"] = row[8]
        task["garageId"] = row[9]
        task["color"] = row[10]
        task["airlineCode"] = row[11]
        task["flightNumber"] = row[12]
        task["terminal"] = row[13]
        tasks.append(task)

    ret["scheduledTasks"] = tasks
    return

def readPersonScheduledTasks(j):
    personId = j["personId"]
    ret = HCommon.getSuccessReturn()
    populatePersonTasks(ret, personId)
    return ret

def applyManualCharge(j):
    personId = j["personId"]
    dbBookingId = j["bookingId"]
    chargeAmount = int(j["chargeAmount"])
    tipAmount = int(j["tipAmount"])

    totalAmount = chargeAmount + tipAmount
    totalAmount = totalAmount * 100

    row = HCommon.execProcOneRow("call updateCityCheckinCharged(%s,%s,%s,%s)",(str(personId),str(dbBookingId),str(chargeAmount),str(tipAmount)))
    stripeCustomerToken = row[1]

    if HCommon.isDev():
        stripe.api_key = "sk_test_JkxVs4tQAyfdfspy4GXnqQEd"
    else:
        stripe.api_key = "sk_live_Vz9P2rMdfp108PwJHhLg8Xp6"

    ret = HCommon.getSuccessReturn()

    if row[0]==1:
        try:
            stripe.Charge.create(
                amount=totalAmount, # 200 is $2.00
                currency="usd",
                customer=stripeCustomerToken,
                description="ValetAnywhere Services"
            )
            return ret
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print "error in charging stripe" + str(exc_value)
            ret = HCommon.setErrorJson(600, "Unable to charge customer via stripe, please look at Stripe log from Stripe web site for more info." + str(exc_value))
            row = HCommon.execProcOneRow("call updateCityCheckinSetUncharged(%s)",(str(dbBookingId)))

    return ret

def applyVaultCharge(j):
    personId = j["personId"]
    personVaultId = j["personVaultId"]
    chargeAmount = int(j["amount"])

    row = HCommon.execProcOneRow("call CreatePersonVaultCharge(%s,%s,%s)",(str(personId),str(personVaultId),str(chargeAmount)))
    vaultChargeId = row[0]
    stripeCustomerToken = row[1]

    if HCommon.isDev():
        stripe.api_key = "sk_test_JkxVs4tQAyfdfspy4GXnqQEd"
    else:
        stripe.api_key = "sk_live_Vz9P2rMdfp108PwJHhLg8Xp6"

    ret = HCommon.getSuccessReturn()

    if vaultChargeId > 0:
        try:
            totalAmount = chargeAmount * 100

            stripe.Charge.create(
                amount=totalAmount, # 200 is $2.00
                currency="usd",
                customer=stripeCustomerToken,
                description="ValetAnywhere Services"
            )
            return ret
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print "error in charging stripe" + str(exc_value)
            ret = HCommon.setErrorJson(600, "Unable to charge customer via stripe, please look at Stripe log from Stripe web site for more info." + str(exc_value))
            row = HCommon.execProcOneRow("call DeletePersonVaultCharge(%s)",(str(vaultChargeId)))

    return ret

def readVaultCoverage(j):
    lat = j["latitude"]
    lng = j["longitude"]

    raw = findVaultCoverage(lat, lng)
    if raw is None:
        return HCommon.setErrorJson(201, "Your location is not within our coverage zone. Interest for coverage in your area has been noted for possible future service.")
    else:
        ret = HCommon.getSuccessReturn()

        hours = {}
        hours["openTime"] = raw[2]
        hours["closeTime"] = raw[3]
        hours["utcOffset"] = raw[4]

        price = {}
        price["id"] = raw[6]
        price["type"] = raw[7]
        price["amount"] = raw[8]
        price["description"] = raw[9]
        price["additionalRoundTripCharge"] = raw[10]
        price["additionalRoundTripSummary"] = raw[11]
        price["roundTripSummary"] = raw[12]

        ret["hours"] = hours
        ret["price"] = price
        ret["poly"] = raw[5]
        ret["carToValetLeadTimeMinutes"] = raw[13]
        ret["carToCustomerLeadTimeMinutes"] = raw[14]

        quota = {}
        quota["in"] = raw[15]
        quota["out"] = raw[16]
        quota["unitCode"] = raw[17]

        ret["parkingQuota"] = quota

        ret["homeRadiusMeters"] = raw[18]
        ret["centerLatitude"] = raw[19]
        ret["centerLongitude"] = raw[20]

        return ret

def readVaultInfo(j):
    personId = j["personId"]
    carId = j["carId"]
    vault = getVaultInfo(personId, carId, False)

    if "id" in vault:
        ret = HCommon.getSuccessReturn()
        ret["vault"] = vault
        return ret
    else:
        return HCommon.setErrorJson(202, "This account with this car is not subscribed to monthly service.")


