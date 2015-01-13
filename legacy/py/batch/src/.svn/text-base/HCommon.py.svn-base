#!/usr/bin/python
import MySQLdb
import cgi
import json
import urllib2
import datetime
import memcache
import uuid
import random
import math
import logging
import AWSEmail
import pytz

ENV="DEV"
IS_SIMULATION=False

MSG_ASSIGN_DROPOFF=1
MSG_ASSIGN_CHECKOUT=2
MSG_BOOK_STATE_UPDATE=3
MSG_VALET_STATE_UPDATE=4
MSG_CUSTOMER_LOC_UPDATE=5
MSG_VALET_LOC_UPDATE=6

#Web Sockets messages:
WS_CUSTOMER_LOCATION = 1
WS_BOOK_STATE_CHANGE = 2
WS_VALET_STATE_CHANGE = 3
WS_VALET_ASSIGNMENT = 4
WS_NO_AVAILABLE_VALET = 5
WS_VALET_LOCATION = 6

_memCache = None

def isDev():
	if ENV=="DEV":
		return True
	else:
		return False

def getTemplatePath():
    return "/srv/www/devweb/batch/templates/"

def getDbConnection():
	db = None;
	if isDev()==True:
		db=MySQLdb.connect(host="vany-dev.cnfbnfdkgiuy.us-west-2.rds.amazonaws.com", user = "vanyroot", passwd = "smrtguard1022", db = "Hermis")
	else:
		db=MySQLdb.connect(host="prod.cnfbnfdkgiuy.us-west-2.rds.amazonaws.com", user = "prod_root", passwd = "hermis1022", db = "Hermis")
	return db

def getMemCache():
        global _memCache
        
        if (_memCache is None):
            if isDev()==True:
                    _memCache =  memcache.Client(['hermiscache.iwaxci.cfg.usw2.cache.amazonaws.com:11211'], debug=0)
            else:
                    _memCache = memcache.Client(['prodcache.iwaxci.cfg.usw2.cache.amazonaws.com:11211'], debug=0)
        
        return _memCache
    
def getWebSocketServerHost(useSSL):
	if isDev()==True:
            if useSSL==1:
		return 'wss://54.191.94.243:8686/s?id=111'
            else:
		return 'ws://54.191.94.243:8989/s?id=111'
	else:
            if useSSL==1:
		return 'wss://54.191.3.38:8686/s?id=111'
            else:
		return 'ws://54.191.3.38:8989/s?id=111'

def getCacheValue(key):
	mc = getMemCache()
	useKey = "DEV_" + key if ENV=="DEV" else key

	value = mc.get(useKey)
	return str(value) if value is not None else ""

def getCacheValueJson(key):
	mc = getMemCache()
	useKey = "DEV_" + key if ENV=="DEV" else key

	value = mc.get(useKey)
	if value is None:
		return None
	else:
		return json.loads(value)
	
def setCacheValue(key, value):
	mc = getMemCache()
	useKey = "DEV_" + key if ENV=="DEV" else key
	mc.set(useKey, value, time=1209600)

def setTenMinutesCache(key, value):
	mc = getMemCache()
	useKey = "DEV_" + key if ENV=="DEV" else key
	mc.set(useKey, value, time=600)

def getTenMinutesCache(key):
	mc = getMemCache()
	useKey = "DEV_" + key if ENV=="DEV" else key

	value = mc.get(useKey)
        return value

def setError(code, errorText):
	return '{"returnCode":' + str(code) + ', "errorMessage": "' + str(errorText) + '"}'

def setErrorJson(code, errorText):
        ret = {}
        ret["returnCode"] = code
        ret["errorMessage"] = errorText
        return ret
    
def appendProcResultJson(ret, entity, proc,args):
	db=getDbConnection()
	c=db.cursor()
        print str(args)
	if len(args) > 0:
            c.execute(proc,args)
	else:
            c.execute(proc)
	rows=c.fetchall()
	field_names = [i[0] for i in c.description]
	c.close()
	db.commit()
	db.close()
	
	field_list = []
	for field in field_names:
		field_list.append(field)
		
	rowarray_list = []
	for row in rows:
		rowList=list(row)
		rowarray_list.append(rowList)

        entityResult = {}
        entityResult["columnNames"] = field_list
        entityResult["rows"] = rowarray_list
        
        ret[entity] = entityResult
	return ret
	
def getJsonFromProc(proc,args):
	db=getDbConnection()
	c=db.cursor()
	if len(args) > 0:
		c.execute(proc,args)
	else:
		c.execute(proc)
	rows=c.fetchall()
	field_names = [i[0] for i in c.description]
	c.close()
	db.commit()
	db.close()
	
	field_list = []
	for field in field_names:
		field_list.append(field)
		
	j = json.dumps(field_list)

	rowarray_list = []
	for row in rows:
		rowList=list(row)
		rowarray_list.append(rowList)

	j2 = json.dumps(rowarray_list)

	ret = '"columnNames":' + j + ', "rows":' + j2
	return ret
	
def execProcOneRow(proc,args):
	db=getDbConnection()
	c=db.cursor()
	if len(args) > 0:
		c.execute(proc,args)
	else:
		c.execute(proc)
	row=c.fetchone()
	c.close()
	db.commit()
	db.close()
	return row

def execProcManyRow(proc,args):
	db=getDbConnection()
	c=db.cursor()
	if len(args) > 0:
		c.execute(proc,args)
	else:
		c.execute(proc)
	rows=c.fetchall()
	c.close()
	db.commit()
	db.close()
	return rows

def execProcManyRowToArrays(proc,args):
	rows = execProcManyRow(proc,args)
	rowarray_list = []
	for row in rows:
		rowList=list(row)
		rowarray_list.append(rowList)
	return rowarray_list
		
def updateProc(proc,args):
	db=getDbConnection()
	c=db.cursor()
	c.execute(proc,args)
	c.close()
	db.commit()
	db.close()

def getFlightStatus(bookId,useCache):
	mc = getMemCache()

	if useCache:
#		print "getting from cache"
		statusData = mc.get(bookId)
		if statusData is not None:
			return statusData
			
	aInfo=getJsonFromProc("call ReadBookingArrivalInfo(%s)", (bookId))
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
	
def getLogger():
    logger = logging.getLogger('booking')
    handler = logging.FileHandler('booking.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger

def getSuccessReturn():
    ret = {}
    ret["returnCode"] = 0
    return ret

def sendEmail(emailAddress, subject, body):
    if isDev():
        bcc = "dev@valetanywhere.com"
        if emailAddress == "valetsupport@valetanywhere.com":
            emailAddress = "dev@valetanywhere.com"
            
        if emailAddress == "support@valetanywhere.com":
            emailAddress = "dev@valetanywhere.com"
            
        AWSEmail.sendemail2(emailAddress, bcc, "DEV - " + subject, body)
    else:
        bcc = "valetsupport@valetanywhere.com"
        AWSEmail.sendemail2(emailAddress, bcc, subject, body)
        
    return

def replaceVariables(txt, vars):
    for var in vars:
        sVar = var.encode('ascii', 'xmlcharrefreplace')
        txt = txt.replace("#VANY#", sVar, 1)
    return txt

def toStdTime(milTime):
    sHr = milTime[:2]
    hr = int(sHr)
    if hr > 12:
        hr = hr - 12
        return str(hr) + milTime[2:] + " PM"
    elif hr==12:
        return str(hr) + milTime[2:] + " PM"
    else:
        return milTime + " AM"

def add_month_year(strDate, years=0, months=0):
    try:
        date = datetime.datetime.strptime(strDate, '%Y-%m-%d %H:%M')

        year, month = date.year + years, date.month + months + 1
        dyear, month = divmod(month - 1, 12)
        rdate = datetime.date(year + dyear, month + 1, 1) - datetime.timedelta(1)
        nextDate = rdate.replace(day = min(rdate.day, date.day))

        return str(nextDate) + strDate[-6:]
    except:
        return ""

def strToDate(str):
    return datetime.datetime.strptime(str, '%Y-%m-%d %H:%M')

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

def formatSubject(subject):
    if isDev():
        return "Dev - " + subject
    else:
        return subject


# Below functions are wsgi handlers - direct translation from the previous scripts
# --------------------------------------------------------------------------------
def readSp(j):
    entities=j["entities"]
    sps=j["sps"]

    aEntities=entities.split(',')
    aSps=sps.split(',')

    high=len(aEntities)

    ret = getSuccessReturn()
    for i in range(high):
        appendProcResultJson(ret, aEntities[i], "call " + aSps[i] + "()", ())

    return ret

