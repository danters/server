#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HCommon
import time
import datetime
import pytz
import HCustomer
import calendar
import re


def fromDbDateToEST(utcStr):
    gmt = pytz.timezone('UTC')
    eastern = pytz.timezone('US/Eastern')
    time = utcStr + " UTC"

    date = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S UTC')
    dategmt = gmt.localize(date)
    dateeastern = dategmt.astimezone(eastern)
    estTime = str(dateeastern)
    estTime = estTime[:16]
    return estTime

dtTime = "2014-09-24 16:42:13"
print fromDbDateToEST(dtTime)

j={}
j["mobile"] = "7328229112"
#ret = HCustomer.smsSecurityCode(j)
#print str(ret)
print len(str(j))


def add_month_year(strDate, years=0, months=0):
    try:
        date = datetime.datetime.strptime(strDate, '%Y-%m-%d %H:%M:%S')

        year, month = date.year + years, date.month + months + 1
        dyear, month = divmod(month - 1, 12)
        rdate = datetime.date(year + dyear, month + 1, 1) - datetime.timedelta(1)
        nextDate = rdate.replace(day = min(rdate.day, date.day))

        return str(nextDate) + strDate[-6:]
    except:
        return ""

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

def dbDateToEST_String(utcStr):
    gmt = pytz.timezone('UTC')
    eastern = pytz.timezone('US/Eastern')
    utcTime = utcStr + " UTC"

    utcDate = datetime.datetime.strptime(utcTime, '%Y-%m-%d %H:%M UTC')
    dategmt = gmt.localize(utcDate)
    dateeastern = dategmt.astimezone(eastern)
    estTime = str(dateeastern)
    estTime = estTime[:16]
    return estTime

def dbDateToEST(utcStr):
    gmt = pytz.timezone('UTC')
    eastern = pytz.timezone('US/Eastern')
    utcTime = utcStr + " UTC"

    utcDate = datetime.datetime.strptime(utcTime, '%Y-%m-%d %H:%M UTC')
    dategmt = gmt.localize(utcDate)
    dateeastern = dategmt.astimezone(eastern)
    return dateeastern
    
    
    
def TestBookingId():
    dbBookingId = 6709
    bookingId = 67093

    print "serviceType=3"
    print "db bookingId=" + str(dbBookingId)

    print "combined bookingId=" + str(bookingId)
    print "make db id into combinedBooking Id=" + str(convertToBookingId(dbBookingId, 3))

    print "extract service type=" + str(getServiceType(bookingId))

    print "extract booking id=" + str(getDbBookingId(bookingId))



#Christmas Block Period
#sBlockStartTime = "2014-12-24 22:00"
#sBlockEndTime = "2014-12-26 12:00"

#New Year Block Period
#sBlockStartTime = "2014-12-31 22:00"
#sBlockEndTime = "2015-01-02 12:00"

sBlockStartTime = "2014-12-22 21:00"
sBlockEndTime = "2014-12-22 21:56"

blockStartTime = dbDateToEST(sBlockStartTime)
blockEndTime = dbDateToEST(sBlockEndTime)

print "start: " + str(blockStartTime)
print "end: " + str(blockEndTime)

now = datetime.datetime.utcnow()
sNow = str(now)
print "Now=" + sNow
sNow = sNow[:16]
print "Now after :16 =" + sNow
estNow = dbDateToEST(sNow)
print "EST Now: " + str(estNow)


if estNow >= blockStartTime and  estNow <= blockEndTime:
    print "Current Time within block time"
    
else:
    print "Current Time outside block time"
    

nextMonthDatetime = add_month_year("2014-12-29 17:54:00",0,1)
print "-------"
print "2015-01-31 11:50"
print str(nextMonthDatetime)
print "-------"


def stripControlCharacters(mobile):
    return re.sub("[^0-9]", "", mobile)        

mobile = "+447580689645"

hasPlus = False

print mobile[:1]
if mobile[:1] == "+":
    hasPlus = True

mobile = stripControlCharacters(mobile)

if hasPlus == True:
    mobile = "+" + str(mobile)
    
print mobile
