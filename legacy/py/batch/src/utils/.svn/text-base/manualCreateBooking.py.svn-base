#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HBook
import json
import HCustomer
import HCommon

j = {}

j['cityCode'] = 'NYC'
j['carId'] = 242
j['personId'] =  558
j['currentLongitude'] =  -73.98939
j['cityBlockId'] =  4
j['priceId'] =  8
j['estNumHours'] =  0
j['currentLatitude'] =  40.744153
j['dropoffLatitude'] =  40.744153
j['dropoffLongitude'] =  -73.98939

#HBook.initiateDropOff(j)
#1114 6th 

def getGarage(id,cityBlockId):
    garages=HCommon.execProcManyRow("call ReadCityBlockGarages(%s)",(str(cityBlockId)))
    for g in garages:
        if g[0]==id:
            return g
    return None

def createManualParkedBooking():
    personId = 750
    valetPersonId=31
    cityCode = "NYC"
    dropoffLongitude = -73.98939
    dropoffLatitude = 40.744153
    currentLongitude = -73.98939
    currentLatitude = 40.744153
    priceId=8
    estNumHours=0
    cityBlockId=4
    carId= 425
    garageId=40
    
    garage = getGarage(garageId,cityBlockId)
    row = HCommon.execProcOneRow("call CreateCityCheckin(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(str(personId),cityCode,str(dropoffLongitude),str(dropoffLatitude),str(currentLongitude),str(currentLatitude),str(priceId),str(estNumHours),str(garageId),str(carId)))
    bookingId = row[0]
    customer = HCustomer.getCustomer(personId)
    if customer is None:
            customerCred = HCommon.getCacheValueJson("CUST_CRED_" + str(personId))

            customer = {}
            customer['personId'] = personId
            customer['bookingId'] = bookingId
            customer['longitude'] = currentLongitude
            customer['latitude'] = currentLatitude
            customer['firstName'] = customerCred["firstName"]
            customer['mobile'] = customerCred["mobile"]
            customerLocation = json.dumps(customer)
            HCustomer.setCustomer(personId, customerLocation)
            customer = HCustomer.getCustomer(personId)

    customer["bookingId"] = bookingId
    customer["serviceType"] = HBook.SERVICE_NOW
    customer["latitude"] = currentLatitude
    customer["longitude"] = currentLongitude
    customerLocation = json.dumps(customer)
    HCustomer.setCustomer(personId, customerLocation)

    codeWord = HBook.getCodeWord()

    booking = {}
    booking['id'] = bookingId
    booking['serviceType'] = HBook.SERVICE_NOW
    booking['customerPersonId'] = personId
    booking['latitude'] = dropoffLatitude
    booking['longitude'] = dropoffLongitude
    booking['valetPersonId'] = valetPersonId
    booking['inValetId'] = valetPersonId
    booking['inValetName'] = "Will"
    booking['codeWord'] = codeWord
    booking['state'] = HBook.BOOK_STATE_CAR_PARKED
    booking['priceId'] = priceId
    booking['estNumHours'] = estNumHours
    booking['priceId'] = priceId
    booking['garage'] = garage
    booking['cityBlockId'] = cityBlockId
    booking['carId'] = carId

    bookingText = json.dumps(booking)
    HBook.setBooking(bookingId, bookingText)
    return


createManualParkedBooking()