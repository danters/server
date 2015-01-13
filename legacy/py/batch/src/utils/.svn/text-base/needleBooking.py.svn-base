#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HBook
import json
import HCustomer
import HCommon


def getGarage(id,cityBlockId):
    garages=HCommon.execProcManyRow("call ReadCityBlockGarages(%s)",(str(cityBlockId)))
    for g in garages:
        if g[0]==id:
            garageJson = {}
            garageJson['id'] = g[0]
            garageJson['name'] = g[1]
            garageJson['latitude'] = g[2]
            garageJson['longitude'] = g[3]
            garageJson['phone'] = g[4]
            garageJson['address'] = g[5]
            return garageJson            
    return None

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
    
bookingId = 298
codeWord = HBook.getCodeWord()

garage = getGarage(garageId,cityBlockId)
print str(garage)

booking = {}
booking['id'] = bookingId
booking['serviceType'] = HBook.SERVICE_NOW
booking['customerPersonId'] = personId
booking['latitude'] = dropoffLatitude
booking['longitude'] = dropoffLongitude
booking['valetPersonId'] = valetPersonId
booking['inValetId'] = valetPersonId
booking['inValetName'] = "Chris"
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
