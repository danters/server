#!/usr/bin/python
import HCommon
import HValet
import HBook
import json
import memcache
import uuid
import datetime
import twilioPack
import sys, traceback
import stripe
import re
import random

def getCustomer(personId):
	key = "CUST_" + str(personId)
        customer = HCommon.getCacheValueJson(key)
        
        #backward compatibility code
        if customer is not None:
            if "carId" in customer and "preferredCarId" not in customer:
                customer["preferredCarId"] = customer["carId"]
               
        return customer

def getCustomerCred(personId):
	key = "CUST_CRED_" + str(personId)
	ret = HCommon.getCacheValueJson(key)
	return ret
	
def setCustomerCred(personId, cred):
	key = "CUST_CRED_" + str(personId)
	HCommon.setCacheValue(key, cred)
		
def getAndValidateCustomerCred(personId,email,authToken):
        
	ret = getCustomerCred(personId)
	
        preferredCarId = 0
        addReferralAmount(ret)
        
	if ret is None:
            return None
	else:
            if ret["authToken"] != authToken:
                return None
            
            if "preferredCarId" in ret:
                preferredCarId = ret["preferredCarId"]
            else:
                if "carId" in ret:
                    preferredCarId = ret["carId"]
                
            if preferredCarId > 0:
                stuffCarInfo(ret,preferredCarId)

            customer = getCustomer(personId)
            if customer is None:
                customer = {}
                customer["personId"] = personId
                customer["bookingId"] = 0
                customer["latitude"] = 0
                customer["longitude"] = 0
                customer["firstName"] = ret["firstName"]
                customer["mobile"] = ret["mobile"]
                customerLocation = json.dumps(customer)
                setCustomer(personId, customerLocation)


            bookingId = customer["bookingId"]
            booking = None
            if bookingId > 0:
                booking = HBook.getBooking(bookingId)
                
                if booking is None:
                    ret["bookingId"] = 0
                else:
                    if booking["state"] < HBook.BOOK_STATE_CANCELLED:
                        valetId = booking["valetPersonId"]
                        valet = HValet.getValet(valetId)

                        ret["bookingId"] = customer["bookingId"]

                        if valet is None:
                                valet = {}

                        ret["valetPersonId"] = valetId
                        booking["valetAssigned"] = valet
                        booking["valet"] = valet
                        booking['customerLatitude'] = customer["latitude"]
                        booking['customerLongitude'] = customer["longitude"]
                        ret["booking"] = booking
                        ret["valetAssigned"] = valet
                    else:
                        ret["bookingId"] = 0
            else:
                    ret["bookingId"] = 0
                    
        ret["vault"] = HBook.getVaultInfo(personId, preferredCarId,True)
        HBook.populatePersonTasks(ret, personId)

	
	return ret

def addReferralAmount(ret):
    ret["giftForFriend"] = 40
    ret["giftForUser"] = 40
    return

def setCustomer(personId,value):
	key = "CUST_" + str(personId)
	HCommon.setCacheValue(key, value)

def setUserToken(email, personId, lastName, firstName, mobile, paymentInfo, countryCode,carId,referCode,zipCode,phoneVerified,address,homeLat,homeLng):
	jCustomer = getCustomer(personId)
	
	print str(jCustomer)
	if jCustomer is None:
            customer = {}
            customer["personId"] = personId
            customer["bookingId"] = 0
            customer["latitude"] = 0
            customer["longitude"] = 0
            customer["preferredCarId"] = carId
            customer["firstName"] = str(firstName)
            customer["mobile"] = str(mobile)
            customerLocation = json.dumps(customer)
            setCustomer(personId, customerLocation)
	
	key = "CUST_CRED_" + str(personId)
	token = uuid.uuid4()
	ret = {}
	ret["returnCode"] = 0
	ret["personId"] = personId
        ret["email"] = email
	ret["lastName"] = str(lastName)
	ret["firstName"] = str(firstName)
	ret["mobile"] = str(mobile)
	ret["paymentInfo"] = str(paymentInfo)
	ret["countryCode"] = str(countryCode)
	ret["authToken"] = str(token)
	ret["preferredCarId"] = carId
        ret["referCode"]=str(referCode)
        ret["zipCode"] = zipCode
        ret["phoneVerified"] = phoneVerified
        ret["address"] = address
        ret["homeLat"] = homeLat
        ret["homeLng"] = homeLng
	
	print "1"
	saveData = json.dumps(ret)
	HCommon.setCacheValue(key,saveData)

	if jCustomer is None:
            ret["bookingId"] = 0
	else:
            bookingId = jCustomer["bookingId"]
            if bookingId > 0:
                booking = HBook.getBooking(bookingId)
                
                if booking is None:
                    ret["bookingId"] = 0
                else:
                    if booking["state"] < HBook.BOOK_STATE_CANCELLED:
                        valetId = booking["valetPersonId"]
                        valet = None
                        if valetId > 0:
                            valet = HValet.getValet(valetId)
                        else:
                            valet = {}
                            valetId = 0

                        ret["bookingId"] = jCustomer["bookingId"]

                        ret["valetPersonId"] = valetId
                        booking["valetAssigned"] = valet
                        booking["valet"] = valet
                        ret["booking"] = booking
                        ret["valetAssigned"] = valet
                    else:
                        ret["bookingId"] = 0
            else:
                print "2"
                ret["bookingId"] = 0
	
	return ret

def getCarInfo(carId):
    row=HCommon.execProcOneRow("call ReadCar(%s)",(str(carId)))
    return row

def stuffCarInfo(ret,carId):
    row = getCarInfo(carId)
    car = {}
    car["carId"] = carId
    car["make"] = row[0]
    car["model"] = row[1]
    car["color"] = row[2]
    car["plate"] = row[3]
    car["year"] = row[4]
    car["state"] = row[6]
    ret["preferredCar"] = car
    return

def clearAllCustomerCache():
	mc = HCommon.getMemCache()
	rows=HCommon.execProcManyRow("call ReadPersons()",())
	for row in rows:
		key = "CUST_CRED_" + str(row[0])
		useKey = "DEV_" + key if HCommon.isDev() else key
		mc.delete(useKey)

		key = "CUST_" + str(row[0])
		useKey = "DEV_" + key if HCommon.isDev() else key
		mc.delete(useKey)
		
def clearSingleCustomerCache(id):
	mc = HCommon.getMemCache()
	key = "CUST_CRED_" + str(id)
	useKey = "DEV_" + key if HCommon.isDev() else key
	mc.delete(useKey)

	key = "CUST_" + str(id)
	useKey = "DEV_" + key if HCommon.isDev() else key
	mc.delete(useKey)

# Below functions are rest functions - direct translation from the previous scripts
# --------------------------------------------------------------------------------
def login(j):
    email = j["email"]
    password = j["password"]
    deviceInfo = ""
    if "deviceType" in j:
        deviceInfo = j["deviceType"]
        deviceInfo = deviceInfo.encode('ascii', 'xmlcharrefreplace')


    row = HCommon.execProcOneRow("call ReadPerson(%s,%s,%s)",(email,password,deviceInfo))

    if row is None:
        return HCommon.setErrorJson(2,"Email address or password not found")
    else:
        ret = setUserToken(email, row[0], row[1], row[2], row[3], row[4], row[5], row[6],row[7],row[13],row[14],row[15],row[17],row[18])
        car = {}
        car["carId"] = row[6]
        car["make"] = row[8]
        car["model"] = row[9]
        car["color"] = row[10]
        car["plate"] = row[11]
        car["year"] = row[12]
        car["state"] = row[16]
        ret["preferredCar"] = car
        ret["vault"] = HBook.getVaultInfo(row[0], row[6], True)
        personId = row[0]
        HBook.populatePersonTasks(ret, personId)
        addReferralAmount(ret)

        return ret

def readCredits(j):
    personId=j["personId"]
    #row= HCommon.execProcManyRow("call ReadPersonReferrals(%s)",(str(personId)))
    ret = HCommon.getSuccessReturn()
    HCommon.appendProcResultJson(ret, "credits", "call ReadPersonReferrals(%s)",(str(personId)))
    return ret

def isInt(val):
    try:
        return val == int(val)
    except:
        return False

def addCar(j):
    make=j["make"]
    model=j["model"]
    color=j["color"]
    personId=j["personId"]

    plate=None
    year=None
    if "plate" in j:
        plate = j["plate"]
        if len(plate)==0:
            plate=None
    if "year" in j:
        year = j["year"]
        if isInt(year):
            if year==0:
                year = None
        else:
            if len(year)==0:
                year = None
        
    result = HCommon.execProcOneRow("call CreateCar(%s,%s,%s,%s,%s,%s)",(make,model,color,plate,str(year),personId))
    #update the cache and set the new car to the current car
    customer = getCustomer(personId)
    if customer is not None:
        customer["preferredCarId"] = result[0]
        
        customertext = json.dumps(customer)
        setCustomer(personId, customertext)
        
    ret = {}
    ret["returnCode"] = 0
    ret["carId"] = result[0]
    return ret

def emailResetPwd(j):
    ret = HCommon.getSuccessReturn()
    email=j["email"]
    email = email.lower()
    row = HCommon.execProcOneRow("call ReadPersonCountByEmail(%s)",(email))
    
    if row[0] > 0:
        key = uuid.uuid4()
        HCommon.setCacheValue(str(key), email)

        #SENDING EMAIL OUT
        templatePath = HCommon.getTemplatePath() + 'resetPwd.txt'

        if HCommon.isDev():
            templatePath = HCommon.getTemplatePath() + 'resetPwdDev.txt'

        fp = open(templatePath, 'r')
        msg = fp.read() % (email, str(key), email, str(key))
        fp.close()
        HCommon.sendEmail(email, "ValetAnywhere Alert - Credentials Change", msg)

        ret["isEmailSent"] = True
    else:
        ret =  HCommon.setErrorJson(98,"No account is associated with this email.");
        ret["isEmailSent"] = False
        
    return ret

def pwdReset(j):
    email = str(j["email"])
    password = str(j["password"])
    authToken = str(j["authToken"])

    ret = HCommon.getSuccessReturn()

    cachedEmail = HCommon.getCacheValue(authToken)
    if cachedEmail != None and cachedEmail==email:
        rowUpdated = HCommon.execProcOneRow("call UpdatePersonPassword(%s,%s)",(email,password))
        if (rowUpdated > 0):
            ret["isPasswordReset"] = True
        else:
            ret["returnCode"] = 1
            ret["errorMessage"] = "Email not found"
    else:
        ret["returnCode"] = 2
        ret["errorMessage"] = "AuthToken expired"
    
    return ret

def readCar(j):
    ret = HCommon.getSuccessReturn()
    carId = j["carId"]
    result = HCommon.execProcOneRow("call ReadCar(%s)",str(carId))
    car = {}
    car["make"] = result[0]
    car["model"] = result[1]
    car["color"] = result[2]
    car["plate"] = result[3]
    car["year"] = result[4]
    car["state"] = result[6]
    car["carId"] = carId
    ret["car"] = car
    return ret


def readCars(j):
    ret = HCommon.getSuccessReturn()
    ret["cars"] = []
    i = 0
    personId = j["personId"]
    result = HCommon.execProcManyRow("call ReadCars(%s)",str(personId))
    while i < len(result) is not None:
        currCar = result[i]
        car = {}
        car["carId"] = currCar[0]
        car["make"] = currCar[1]
        car["model"] = currCar[2]
        car["color"] = currCar[3]
        car["plate"] = currCar[4]
        car["year"] = currCar[5]
        car["preferredCar"] = currCar[6]
        ret["cars"].append(car)
        i += 1
        
    return ret


def readUpdateLatestLocation(j):
    customer=j["customer"]
    personId=customer["personId"]
    
    ret = HCommon.getSuccessReturn()
    if personId==0:
        return ret
    
    customerLatitude=customer["latitude"]
    customerLongitude=customer["longitude"]

    ret["bookingId"] = 0
    ret["valetAssigned"] = {}

    state=0

    HBook.updateLocation(True, personId, customerLatitude, customerLongitude)

    bookingId = 0
    booking = None
    
    customerCache = getCustomer(personId)

    if customerCache is None:
        return HCommon.setErrorJson(99,"Customer personId does not exists. Please try to login again")

    bookingId = customerCache["bookingId"]
    if bookingId > 0:
        booking = HBook.getBooking(bookingId)
        
    if booking is not None:
        booking['customerLatitude'] = customer["latitude"]
        booking['customerLongitude'] = customer["longitude"]
        state = booking['state']

        if state < HBook.BOOK_STATE_CANCELLED:
            valetPersonId = booking['valetPersonId']

            valet = HValet.getValet(valetPersonId)
            ret["bookingId"] = bookingId
            ret["valetAssigned"] = valet
            booking["valetAssigned"] = valet
            booking["valet"] = valet
            ret["booking"] = booking
        elif state == HBook.BOOK_STATE_COMPLETED:
            ret["bookingId"] = bookingId
            ret["booking"] = booking
        

    return ret

def readPaymentInfo(j):
    personId=j["personId"]
    result = HCommon.execProcOneRow("call ReadPaymentInfo(%s)",str(personId))
    ret = HCommon.getSuccessReturn()
    
    if result is not None:
        custId = result[0]
        pos = custId.find("cus_")
        if pos >= 0:
            if HCommon.isDev():
                stripe.api_key = "sk_test_JkxVs4tQAyfdfspy4GXnqQEd"
            else:
                stripe.api_key = "sk_live_Vz9P2rMdfp108PwJHhLg8Xp6"
            customer = stripe.Customer.retrieve(custId)
            ret["stripeCustomer"] = customer
        else:
            ret["stripeCustomer"] = {}
    else:
        ret["stripeCustomer"] = {}

    HCommon.appendProcResultJson(ret, "credits", "call ReadPersonReferrals(%s)",(str(personId)))
    HCommon.appendProcResultJson(ret, "vaultTracking", "call ReadPersonVaultTracking(%s)",(str(personId)))
        
    return ret

def vaultWebSignup(j):
    #This is used by the website to do a full signup for monthly
    ret = HCommon.getSuccessReturn()
    templatePath = HCommon.getTemplatePath()
    personId = 0
#    try:
#        print "Into the signup function"
    email=j["email"]
    password=j["password"]
    lastName=str(j["lastName"])
    firstName=str(j["firstName"])
    mobile=j["mobile"]
    mobile = re.sub("[^0-9]", "", mobile)        
    zipCode=j["zipCode"]
    email=j["email"]
    password=j["password"]
    lastName=str(j["lastName"])
    firstName=str(j["firstName"])
    mobile=j["mobile"]
    mobile = re.sub("[^0-9]", "", mobile)        
    zipCode=j["zipCode"]
    address=j["address"]
    address = address.encode('ascii', 'xmlcharrefreplace')
    homeLat=j["homeLat"]
    homeLng=j["homeLng"]
    
    raw = HBook.findVaultCoverage(homeLat, homeLng)
    if raw is None:
        return HCommon.setErrorJson(201, "Your location is not within our coverage zone. Interest for coverage in your area has been noted for possible future service.")
    vaultCoverageId = raw[0]
    
    paymentInfo=""
    countryCode="US"
    referredByCode=""
    if "referredByCode" in j:
        referredByCode = str(j["referredByCode"])
        
    adRefer=""
    phoneVerified = 0
    carId=0

    car = j["car"]
    make=car["make"]
    model=car["model"]
    year=car["year"]
    color=car["color"]
    plate=car["plate"]
    state=car["state"]
    
    partnerCode=""
    if "partnerCode" in j:
        partnerCode = str(j["partnerCode"])

    promoCode = ""
    if "promoCode" in j:
        promoCode = str(j["promoCode"])
    

    result=HCommon.execProcOneRow("call CreatePersonFull(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(email,password,lastName,firstName,mobile,paymentInfo,countryCode,referredByCode,adRefer,zipCode,address,str(homeLat),str(homeLng),make, model, str(year), color, plate, state, partnerCode, promoCode,str(vaultCoverageId)))
    personId=int(result[0])
    if personId > 0:
        referCode = result[1]
        carId = result[2]
        car["carId"] = carId

        print "before setUserToken " + str(carId)
        ret=setUserToken(email, personId, lastName, firstName, mobile, paymentInfo, countryCode,carId,referCode,zipCode,phoneVerified,address,homeLat,homeLng)
        ret["zipCode"] = zipCode
        ret["referCode"] = referCode
        ret["preferredCar"] = car
        ret["address"] = address
        ret["homeLat"] = homeLat
        ret["homeLng"] = homeLng
        print "after setUserToken"

        custCred = getCustomerCred(personId)
        custCred["address"] = address
        custCred["zipCode"] = zipCode
        custCred["homeLat"] = homeLat
        custCred["homeLng"] = homeLng

        sCustCred = json.dumps(custCred)
        setCustomerCred(personId, sCustCred)

        zipCode = ""
        phoneVerified=0
        fp = open(templatePath + 'signupWelcome.html', 'r')
        msg = fp.read()
        
        dummy = ""
        msg = HCommon.replaceVariables(msg, (firstName, dummy))

        fp.close()
        HCommon.sendEmail(email, "Welcome to ValetAnywhere!", msg)

        msg="Please reply 'YES' to this message to verify your account with ValetAnywhere, the best on-demand valet service"
        twilioPack.sendVerifyMessage(mobile, msg)
        
    elif personId==0:
        ret = HCommon.setErrorJson(2,"Email Address  already exists")
    elif personId==-1:
        ret = HCommon.setErrorJson(3,"Phone Number already exists")

    ret["vault"] = {}
    addEmptyScheduledTask(ret)
    return ret
    
#    except:
#	exc_type, exc_value, exc_traceback = sys.exc_info()
#	ret = HCommon.setErrorJson(1,str(exc_value))
        
#    return ret

def addEmptyScheduledTask(ret):
    #emptyScheduledTasks = "{'columnNames': ['Id', 'ServiceType', 'TaskType', 'TaskTime', 'Latitude', 'Longitude', 'CarId', 'Make', 'Model', 'GarageId', 'Color', 'AirlineCode', 'FlightNum', 'Terminal'], 'rows': [] }"
    ret["scheduledTasks"] = []
    return

def signup(j):
    ret = HCommon.getSuccessReturn()
    templatePath = HCommon.getTemplatePath()
    personId = 0
#    try:
#        print "Into the signup function"
    email=j["email"]
    password=j["password"]
    lastName=""
    if "lastName" in j:
        lastName=str(j["lastName"])
        
    firstName=str(j["firstName"])
    mobile=j["mobile"]
    mobile = re.sub("[^0-9]", "", mobile)        

    paymentInfo=""
    countryCode="US"
    referredByCode=""
    if "referredByCode" in j:
        referredByCode = str(j["referredByCode"])
    partnerCode=""
    address=""
    if "address" in j:
        address = j["address"]
        address = address.encode('ascii', 'xmlcharrefreplace')

    carId=0

    if "partnerCode" in j:
        partnerCode = str(j["partnerCode"])

    promoCode = ""
    if "promoCode" in j:
        promoCode = str(j["promoCode"])

    print "partnerCode=" + partnerCode + ", promoCode=" + promoCode

    result=HCommon.execProcOneRow("call CreatePerson(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(email,password,lastName,firstName,mobile,paymentInfo,countryCode,referredByCode,partnerCode,promoCode))
    personId=int(result[0])
    if personId > 0:
        j["personId"] = personId
        referCode = result[1]
        ret["referCode"] = referCode
        zipCode = ""
        phoneVerified=1
        fp = open(templatePath + 'signupWelcome.html', 'r')
        msg = fp.read()

        dummy = ""
        msg = HCommon.replaceVariables(msg, (firstName,dummy))
        fp.close()
        HCommon.sendEmail(email, "Welcome to ValetAnywhere!", msg)

        if "car" in j:
            car = j["car"]
            car["personId"] = personId
            carRet = addCar(car)
            carId = carRet["carId"]
            car["carId"] = carId
            print str(carId)

        print "before setUserToken"
        ret=setUserToken(email, personId, lastName, firstName, mobile, paymentInfo, countryCode,carId,referCode,zipCode,phoneVerified,address,0,0)
        print "after setUserToken"

        if "car" in j:
            ret["preferredCar"] = j["car"]

        if "paymentInfo" in j:
            payInfo = j["paymentInfo"]
            if len(str(payInfo)) > 14:
                print "Payment Info updating"
                payInfo["personId"] = personId
                updatePaymentInfo(payInfo)

    elif personId==0:
        ret = HCommon.setErrorJson(2,"Email Address  already exists")
    elif personId==-1:
        ret = HCommon.setErrorJson(3,"Phone Number already exists")

    ret["vault"] = {}
    addEmptyScheduledTask(ret)
    return ret
    
    #except:
    #exc_type, exc_value, exc_traceback = sys.exc_info()
    #ret = HCommon.setErrorJson(1,str(exc_value))
        
    #return ret

def vaSignup(j):
    ret = HCommon.getSuccessReturn()
    personId = 0
    try:
#        print "Into the signup function"
	email=j["email"]
	password=j["password"]
	lastName=str(j["lastName"])
	firstName=str(j["firstName"])
	mobile=j["mobile"]
        mobile = re.sub("[^0-9]", "", mobile)        
        
	paymentInfo=""
	countryCode="US"
        referredByCode=""
        if "referredByCode" in j:
            referredByCode = str(j["referredByCode"])
	adRefer=""
        carId=0

        result=HCommon.execProcOneRow("call CreatePerson(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(email,password,lastName,firstName,mobile,paymentInfo,countryCode,referredByCode,adRefer))
        personId=int(result[0])
	if personId > 0:
            referCode = result[1]
            ret["referCode"] = referCode
            zipCode = ""
            phoneVerified=1
            address=""
            ret=setUserToken(email, personId, lastName, firstName, mobile, paymentInfo, countryCode,carId,referCode,zipCode,phoneVerified,address,0,0)
            
            if "car" in j:
                car = j["car"]
                car["personId"] = personId
                addCar(car)
                
            result=HCommon.execProcOneRow("call UpdateVerification(%s)",(mobile))
            
	elif personId==0:
            ret = HCommon.setErrorJson(2,"Email Address  already exists")
	elif personId==-1:
            ret = HCommon.setErrorJson(3,"Phone Number already exists")
        
        ret["vault"] = {}
        addEmptyScheduledTask(ret)
        return ret
    
    except:
	exc_type, exc_value, exc_traceback = sys.exc_info()
	ret = HCommon.setErrorJson(1,str(exc_value))
    return ret

def submitTip(j):
    bookingId = j["bookingId"]
    tipAmount = j["tipAmount"]
    serviceType = HBook.getServiceType(bookingId)
    dbBookingId = HBook.getDbBookingId(bookingId)
    
    booking = None
    booking = HBook.getBooking(bookingId)
    
    if booking is None:
        return HCommon.setErrorJson(101,"Unable to find booking " + str(bookingId))
        
    if serviceType == HBook.SERVICE_NOW and booking["state"] < HBook.BOOK_STATE_CAR_IN_TRANSIT:
        return HCommon.setErrorJson(102, "Setting a tip on an invalid state")
        
        
    booking["tipAmount"] = tipAmount
    booking["hasTip"] = True

    if serviceType == HBook.SERVICE_NOW or serviceType == HBook.SERVICE_ADVANCE:
        booking["state"] = HBook.BOOK_STATE_COMPLETED
        HCommon.execProcOneRow("call UpdateCityCheckinTip(%s,%s)",(str(dbBookingId),str(tipAmount)))
    else:
        HCommon.execProcOneRow("call UpdateTaskTip(%s,%s)",(str(dbBookingId),str(tipAmount)))

    sBooking = json.dumps(booking)
    HBook.setBooking(bookingId, sBooking)
    
    ret = HCommon.getSuccessReturn()
    ret["booking"] = booking
    return ret
    
def submitRating(j):
    ret = HCommon.getSuccessReturn()
    bookingId = 0
    if "checkinId" in j:
        bookingId = j["checkinId"]
    else:
        bookingId = j["bookingId"]
    serviceType = HBook.getServiceType(bookingId)
    dbBookingId = HBook.getDbBookingId(bookingId)
    overallValetRating=j["overallStars"]
    row = HCommon.execProcOneRow("call CreateReview(%s,%s,%s)",(str(dbBookingId),str(overallValetRating),str(serviceType)))

    clearCustomerBooking = True
    booking = HBook.getBooking(bookingId)

    if serviceType == HBook.SERVICE_NOW or serviceType == HBook.SERVICE_ADVANCE:
        if booking is not None:
            booking["hasRating"] = True
            booking["state"] = HBook.BOOK_STATE_COMPLETED
            booking["hasTip"] = True
        ret["booking"] = booking
        HBook.clearSingleBookingCache(bookingId)
    else:
        booking["hasRating"] = True
        sBooking = json.dumps(booking)
        HBook.setBooking(bookingId, sBooking)
        if booking["state"]==HBook.BOOK_STATE_COMPLETED or booking["state"]== HBook.BOOK_STATE_CAR_PARKED:
            HBook.clearSingleVaultTaskCache(bookingId)
        else:
            clearCustomerBooking = False
        ret["booking"] = booking
            
    if row is not None and clearCustomerBooking == True:
        personId = row[1]

        customer = getCustomer(personId)
        if customer is not None:
            customer["bookingId"] = 0
            sCustomer = json.dumps(customer)
            setCustomer(personId, sCustomer)

    return ret

def updateCar(j):
    carId=j["carId"]
    make=j["make"]
    model=j["model"]
    color=j["color"]
    plate=None
    year=None
    if "plate" in j:
        plate = j["plate"]
        if len(plate)==0:
            plate=None
            
    if "year" in j:
        year = j["year"]
        if isInt(year):
            if year==0:
                year = None
        else:
            if len(year)==0:
                year = None
            
    HCommon.execProcOneRow("call UpdateCar(%s,%s,%s,%s,%s,%s)",(carId,make,model,color,plate,str(year)))
    ret = HCommon.getSuccessReturn()
    ret["carId"] = carId
    return ret

def updatePaymentInfo(j):
    personId=j["personId"]
    stripeToken=j["stripeToken"]
    ccEnding=j["ccEnding"]

    ret = HCommon.getSuccessReturn()

    try:

        #creating a customer object. It allows us to charge mulitple times.
        if HCommon.isDev():
            stripe.api_key = "sk_test_JkxVs4tQAyfdfspy4GXnqQEd"
        else:
            stripe.api_key = "sk_live_Vz9P2rMdfp108PwJHhLg8Xp6"

        customer = stripe.Customer.create(
                card=stripeToken,
                description=str(personId)
                )
        customerId=customer.id

        HCommon.updateProc("call UpdatePaymentInfo(%s,%s,%s)",(str(personId),customerId,ccEnding))

        customer = getCustomerCred(personId)
        customer["paymentInfo"] = ccEnding
        sCustomer = json.dumps(customer)
        setCustomerCred(personId, sCustomer)
        return ret
    
    except stripe.error.CardError, e:
        # Since it's a decline, stripe.error.CardError will be caught
        body = e.json_body
        err  = body['error']
        
        ret["returnCode"] = 101
        ret["errorMessage"] = err['message']

        return ret
    except stripe.error.InvalidRequestError, e:
        body = e.json_body
        err  = body['error']
        print str(err)
        ret["returnCode"] = 102
        ret["errorMessage"] = err['message']
        return ret
    except stripe.error.AuthenticationError, e:
        body = e.json_body
        err  = body['error']
        print str(err)
        ret["returnCode"] = 103
        ret["errorMessage"] = err['message']
        return ret
    except stripe.error.APIConnectionError, e:
        body = e.json_body
        err  = body['error']
        print str(err)
        ret["returnCode"] = 104
        ret["errorMessage"] = err['message']
        return ret
    except stripe.error.StripeError, e:
        body = e.json_body
        err  = body['error']
        print str(err)
        ret["returnCode"] = 105
        ret["errorMessage"] = err['message']
        return ret
    except Exception, e:
        body = e.json_body
        err  = body['error']
        print str(err)
        ret["returnCode"] = 106
        ret["errorMessage"] = err['message']
        return ret
    
    return ret
    
def updatePreferredCar(j):
    personId=j["personId"]
    carId=j["carId"]

    HCommon.execProcOneRow("call UpdatePreferredCar(%s,%s)",(str(personId),str(carId)))
    return HCommon.getSuccessReturn()

def updateProfile(j):
    personId=j["personId"]
    email=j["email"]
    mobile=j["mobile"]
    firstName=j["firstName"]
    lastName=j["lastName"]

    cred = getCustomerCred(personId)
    cred["email"] = email
    cred["mobile"] = mobile
    cred["firstName"] = firstName
    cred["lastName"] = lastName

    carId=0
    if "preferredCarId" in j:
        carId = j["preferredCarId"]
        cred["preferredCarId"] = carId
    
    if carId == 0:
        if "preferredCarId" in cred:
            carId = cred["preferredCarId"]
        else:
            if "carId" in cred:
                carId = cred["carId"]
        
    sCred = json.dumps(cred)
    setCustomerCred(personId, sCred)
    
    customer = getCustomer(personId)
    customer["firstName"] = firstName
    customer["mobile"] = mobile
    sCustomer = json.dumps(customer)
    setCustomer(personId, sCustomer)
    
    rowUpdated = HCommon.execProcOneRow("call UpdatePersonProfile(%s,%s,%s,%s,%s,%s)",(str(personId),firstName,lastName,email,mobile,str(carId)))
    ret = HCommon.getSuccessReturn()
    if (rowUpdated < 1):
        ret["returnCode"] = 1
        ret["errorMessage"] = "PersonId not found"

    return ret

def validateCustomerToken(environ):
    sPersonId = str(environ["Personid"])
    #HTTP headers looks like it does not preserve numeric values and convert everything to text
    personId = int(sPersonId)
    authToken = environ["Authtoken"]
    email = environ["Email"]

    customer = getAndValidateCustomerCred(personId, email, authToken)
    if customer is None:
        return HCommon.setErrorJson(1,"Invalid Credentials or Expired Token")
    else:
        return customer
    
    return None
        
def checkVerify(j):
    personId = j["personId"]
    result = HCommon.execProcOneRow("call ReadVerifcation(%s)",str(personId))
    ret = HCommon.getSuccessReturn()
    ret["verified"] = result[0]
    return ret

def sendDropOffMessage(j):
    customerId = j["customerId"]
    valetName=j["valetName"]
    codeWord=j["codeWord"]
    customerId=str(customerId)
    customerInfo = HCommon.execProcOneRow("call ReadPersonbyId(%s)",(customerId))
    customerMobile=str(customerInfo[2])
    if(customerMobile):
        twilioPack.sendMessageDropOff(customerMobile,valetName,codeWord)
    return HCommon.getSuccessReturn()
def sendDownloadLink(j):
    mobile=j["mobile"]
    result=""
    if(mobile):
        result=twilioPack.sendWelcomeLink(str(mobile))
    ret=HCommon.getSuccessReturn()
    ret["Message"]=result
    return ret
def updateTrackingCustomer(j):
    personId=j["personId"]
    customerLatitude=j["latitude"]
    customerLongitude=j["longitude"]
    bookingId=j["bookingId"]
    oldState=j["state"]

    ret = {}
    ret["returnCode"] = 0
    ret["bookingId"] = bookingId
    HBook.updateLocation(True, personId, customerLatitude, customerLongitude)
    if (bookingId > 0):
            booking = HBook.getBooking(bookingId)
            state = ret["state"] = booking["state"]
            if state != HBook.BOOK_STATE_CANCELLED:
                if state > oldState:
                    booking['customerLatitude'] = customerLatitude
                    booking['customerLongitude'] = customerLongitude
                    ret["booking"] = booking
                if state < HBook.BOOK_STATE_CANCELLED:
                    valet = HValet.getValet(booking['valetPersonId'])
                    ret["valetAssigned"] = valet
    return ret

def getPromo(j):
    personId=j["customerId"]
    rows=HCommon.execProcManyRow("call ReadPromoAmt(%s)",(str(personId)))
    ret = HCommon.getSuccessReturn()
    ret["rows"] = rows
    return ret

def validateEmailMobile(j):
    email = j["email"]
    mobile = j["mobile"]
    
    #index=random.randrange(1000,9999)
    #value = str(index)
    #HCommon.setTenMinutesCache(mobile,value)
    
    rows=HCommon.execProcManyRow("call ValidateEmailMobile(%s,%s)",(email,str(mobile)))
    ret = HCommon.getSuccessReturn()
    #if len(rows) > 0:
    #    ret = HCommon.setErrorJson(10,"Email address or Mobile Number already exists")
        
    ret["rows"] = rows
    
    return ret

def readCustomer(j):
    personId=j["personId"]
    customer = getCustomer(personId)
    ret = HCommon.getSuccessReturn()
    ret["customer"] = customer
    return ret

def signupVaultNative(j):
    personId=j["personId"]
    carId=0
    if "carId" in j:
        carId=j["carId"]
    else:
        #get carId from cache
        customer = getCustomer(personId)
        if "preferredCarId" in customer:
            carId=j["carId"]
        
        if carId==0 and "carId" in customer:
            carId=customer["carId"]
        
    address=j["address"]
    address = address.encode('ascii', 'xmlcharrefreplace')
    lat = j["homeLatitude"]
    lng = j["homeLongitude"]
    
    raw = HBook.findVaultCoverage(lat, lng)
    if raw is None:
        return HCommon.setErrorJson(201, "Your location is not within our coverage zone. Interest for coverage in your area has been noted for possible future service.")
    
    vaultCoverageId = raw[0]
    row = HCommon.execProcOneRow("call CreatePersonVaultNative(%s,%s,%s,%s,%s,%s)",(str(personId),str(carId),str(address),str(lat),str(lng),str(vaultCoverageId)))
    ret = HCommon.getSuccessReturn()
    if (row > 0):
        vault = HBook.getVaultInfo(personId, carId,False)

        price = {}
        price["id"] = row[1]
        price["type"] = row[2]
        price["amount"] = row[3]
        price["description"] = row[4]
        price["additionalRoundTripCharge"] = row[5]
        price["additionalRoundTripSummary"] = row[6]
        price["roundTripSummary"] = row[7]
        
        ret["price"] = price
        ret["carToValetLeadTimeMinutes"] = row[8]
        ret["carToCustomerLeadTimeMinutes"] = row[9]
        
        ret["address"] = address
        ret["vault"] = vault
        
        custCred = getCustomerCred(personId)
        custCred["address"] = address
        custCred["homeLat"] = lat
        custCred["homeLng"] = lng
        custCred["vault"] = vault
        
        sCustCred = json.dumps(custCred)
        setCustomerCred(personId, sCustCred)
    else:
        ret["returnCode"] = 1
        ret["errorMessage"] = "PersonId not found"
    
    return ret

def signupVaultHtml5(j):
    personId=j["personId"]
    carId=0
    if "carId" in j:
        carId=j["carId"]
    else:
        #get carId from cache
        customer = getCustomer(personId)
        if "preferredCarId" in customer:
             carId=j["carId"]
        
        if carId==0 and "carId" in customer:
            carId=customer["carId"]
        
    zipCode=j["zipCode"]
    state=j["state"]
    year=j["year"]
    address=j["address"]
    address = address.encode('ascii', 'xmlcharrefreplace')
    make=j["make"]
    model=j["model"]
    plate=j["plate"]
    color=j["color"]
    name=j["name"]
    email=j["email"]
    phone=j["phone"]
    lat = j["homeLat"]
    lng = j["homeLng"]
    promoCode = ""
    if "promoCode" in j:
        promoCode = j["promoCode"]
        
    row = HCommon.execProcOneRow("call CreatePersonVault(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(str(personId),str(carId),str(zipCode),str(name),str(email),str(phone),str(address),str(make),str(model),str(year),str(color),str(plate),str(state),str(lat),str(lng),promoCode))
    ret = HCommon.getSuccessReturn()
    if (row > 0):
        ret["zipCode"] = zipCode
        vault = {}
        vault["id"] = row[0]
        vault["carId"] = carId
        vault["isActive"] = 0
        vault["startDate"] = ""
        vault["carState"] = HBook.VAULT_CARSTATE_WITHCUSTOMER
        vault["promoCode"] = promoCode
        vault["homeLatitude"] = lat
        vault["homeLongitude"] = lng
        vault["homeRadiusMeters"] = 110
        HBook.stuffVaultPrice(vault)

        ret["address"] = address
        ret["homeLat"] = lat
        ret["homeLng"] = lng
        ret["vault"] = vault
        
        custCred = getCustomerCred(personId)
        custCred["address"] = address
        custCred["zipCode"] = zipCode
        custCred["homeLat"] = lat
        custCred["homeLng"] = lng
        custCred["vault"] = vault
        
        sCustCred = json.dumps(custCred)
        setCustomerCred(personId, sCustCred)
    else:
        ret["returnCode"] = 1
        ret["errorMessage"] = "PersonId not found"
    
    return ret

def readVaultTracking(j):
    personId = j["personId"]
    ret = HCommon.getSuccessReturn()
    HCommon.appendProcResultJson(ret, "vaultTracking", "call ReadPersonVaultTracking(%s)",(str(personId)))
    return ret

def apiSignup(j):
    name = j["name"]
    email = j["email"]
    phone = j["phone"]
    company = j["company"]
    companyAddress = j["companyAddress"]
    companyAddress = companyAddress.encode('ascii', 'xmlcharrefreplace')
    
    row=HCommon.execProcOneRow("call CreateApiSignup(%s,%s,%s,%s,%s)",(name,email,phone,company,companyAddress))
    templatePath = HCommon.getTemplatePath()
    fp = open(templatePath + 'apiSignupWelcome.html', 'r')
    msg = fp.read()

    dummy = ""
    msg = HCommon.replaceVariables(msg, (name, dummy))

    fp.close()
    HCommon.sendEmail(email, "Welcome to ValetAnywhere Developer's API Program!", msg)
    return HCommon.getSuccessReturn()

def deleteCar(j):
    carId = j["carId"]
    row=HCommon.execProcOneRow("call DeleteCar(%s)",(str(carId)))
    return  HCommon.getSuccessReturn()
    
    
def smsSecurityCode(j):
    mobile = j["mobile"]
    
    hasPlus = False
    print mobile[:1]
    if mobile[:1] == "+":
        hasPlus = True
        
    mobile = stripControlCharacters(mobile)
    
    if hasPlus == True:
        mobile = "+" + mobile
    print mobile
    
    index=random.randrange(1000,9999)
    value = str(index)
    HCommon.setTenMinutesCache(str(mobile),value)

    ret = HCommon.getSuccessReturn()
    
    msg="Your security code is " + value + ". This code will expire in 10 minutes."
    twilioPack.sendVerifyMessage(mobile, msg)

    return ret

def stripControlCharacters(mobile):
    return re.sub("[^0-9]", "", mobile)        

def validateSecurityCode(j):
    mobile = str(j["mobile"])
    hasPlus = False
    
    print mobile[:1]
    if mobile[:1] == "+":
        hasPlus = True
        
    mobile = stripControlCharacters(mobile)
    
    if hasPlus == True:
        mobile = "+" + mobile
        
    print mobile
        
    securityCode = j["securityCode"]
    
    securityCodeCache = HCommon.getTenMinutesCache(str(mobile))
    
    if str(securityCodeCache) != str(securityCode):
        return HCommon.setErrorJson(11,"Security Code not found for this Mobile phone number.")

    return HCommon.getSuccessReturn()

def resetPassword(j):
    mobile = j["mobile"]
    resetCode = j["securityCode"]
    newPassword = j["newPassword"]
    value = HCommon.getTenMinutesCache(mobile)
    if value!=resetCode:
        return HCommon.setErrorJson(10,"Reset code not valid or expired")

    row=HCommon.execProcOneRow("call UpdatePersonMobile(%s)",(str(mobile),newPassword))
    if row[0]==0:
        return HCommon.setErrorJson(10,"Mobile Number not found")
    
    ret = HCommon.getSuccessReturn()
    
def readPersonVaultCharges(j):
    personId = j["personId"]
    ret = HCommon.getSuccessReturn()
    HCommon.appendProcResultJson(ret, "charges", "call ReadPersonVaultCharges(%s)",(str(personId)))
    return ret

def readPersonVaultTaskHistory(j):
    personId = j["personId"]        
    ret = HCommon.getSuccessReturn()
    HCommon.appendProcResultJson(ret, "tasks", "call ReadPersonVaultTaskHistory(%s)",(str(personId)))
    return ret

def updateVaultSubscription(j):
    personId = j["personId"]
    personVaultId = j["personVaultId"]
    garageId = j["garageId"]
    garageLotNumber = j["garageLotNumber"]
    marketingPartnerCode = j["marketingPartnerCode"]
    marketingPartnerPromoCode = j["marketingPartnerPromoCode"]
    startDate = j["startDate"]
    promisedPrice = j["promisedPrice"]
    address = j["address"]
    lat = j["lat"]
    lng = j["lng"]
    isActive = j["isActive"]
    
    row=HCommon.execProcOneRow("call UpdatePersonVaultSubcription(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(str(personId),str(personVaultId),str(garageId),str(garageLotNumber),str(marketingPartnerCode),str(marketingPartnerPromoCode),str(startDate),str(promisedPrice),str(address),str(lat),str(lng),str(isActive)))
    return HCommon.getSuccessReturn()
    
def deleteAllCustomerBooking(j):
    email = j["email"]
    password = j["password"]
    deviceInfo = ""

    row = HCommon.execProcOneRow("call ReadPerson(%s,%s,%s)",(email,password,deviceInfo))

    if row is None:
        return HCommon.setErrorJson(2,"Email address or password not found")
    else:
        personId = row[0]
        customer = getCustomer(personId)
        customer["bookingId"] = 0
        
        dummy = HCommon.execProcOneRow("call DeletePersonAllTransactions(%s)",(str(personId)))
        
        
        return HCommon.getSuccessReturn()

def deleteCustomerVaultSubscription(j):
    if HCommon.isDev():
        email = j["email"]
        password = j["password"]
        deviceInfo = ""

        row = HCommon.execProcOneRow("call ReadPerson(%s,%s,%s)",(email,password,deviceInfo))
        
        if row is not None:
            personId = row[0]
            row=HCommon.execProcOneRow("call DeletePersonVaultInfo(%s)",(str(personId)))
            return HCommon.getSuccessReturn()
        else:
            return HCommon.setErrorJson(2,"Email address or password not found")
    else:
        return HCommon.setErrorJson(21,"WARNING!!! You're hitting Prod. Request Invalid.")
    
def deleteAccount(j):
    if HCommon.isDev():
        email = j["email"]
        password = j["password"]
        deviceInfo = ""

        row = HCommon.execProcOneRow("call ReadPerson(%s,%s,%s)",(email,password,deviceInfo))
        
        if row is not None:
            row=HCommon.execProcOneRow("call DeletePerson(%s)",(email))
        else:
            return HCommon.setErrorJson(2,"Email address or password not found")
            
        print str(row)
        clearSingleCustomerCache(row)

        return HCommon.getSuccessReturn()
    else:
        return HCommon.setErrorJson(21,"WARNING!!! You're hitting Prod. Request Invalid.")
    
def addWaitList(j):
    cityCode = j["cityCode"]
    contactType = j["contactType"]
    contactInfo = j["contactInfo"]

    try:
        if contactType=="email":
            row = HCommon.execProcOneRow("call CreateEmailInvite(%s,%s)",(cityCode,contactInfo))
        else:
            row = HCommon.execProcOneRow("call CreateMobileInvite(%s,%s)",(cityCode,contactInfo))
            
        templatePath = HCommon.getTemplatePath() + 'inviteConfirm.html'
        
        fp = open(templatePath, 'r')
        msg = fp.read()
        fp.close()
        HCommon.sendEmail(contactInfo, "You are added to ValetAnywhere Invitation List", msg)
            
    except:
        return HCommon.setErrorJson(22,"Already in the waiting list")



    return HCommon.getSuccessReturn()
    
    