#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HCommon
import HBook
import datetime
import time
import calendar
import pytz

supportEmail = "support@valetanywhere.com"

def mainProcess():
    garageMap = {}
    garages=HCommon.execProcManyRow("call ReadAllDistinctGarages()",())
    for g in garages:
        garageMap[str(g[0])]= g

    tasks=HCommon.execProcManyRow("call ReadAllActiveTasks()",())
    now = datetime.datetime.utcnow()
    sNow = str(now)
    sNow = sNow[:16]
    nowEST_str = dbDateToEST_String(sNow)
    nowESTDate = nowEST_str[:10]
    nowESTTime = nowEST_str[11:]
    
    stdTime = toStdTime(nowESTTime)
    
    nowEST = dbDateToEST(sNow)
    tomorrowDate = nowEST + datetime.timedelta(days=1)
    sTomorrowDate = str(tomorrowDate)
    nextDayDate = sTomorrowDate[:10]

    print "Dates Now,Now+1: " + nowESTDate +  " " + nowESTTime + ", " + nextDayDate

    processAdvanceConversion(tasks, nowEST)

    if nowESTTime=="01:00" or nowESTTime=="06:00" or nowESTTime=="12:00":
        processTodaysTasks(tasks, garageMap, nowESTDate, stdTime)
    
    if nowESTTime=="18:00":
        processVaultDayReminder(tasks, nextDayDate)
    
    processVaultExpired(tasks, garageMap, nowEST, nowESTDate, stdTime)
    processVaultThreeHoursReminder(tasks, nowEST, nowESTDate)
    processAdvanceThirtyMins(tasks, garageMap, nowEST, nowESTDate, stdTime)

    return


def replaceVariables(txt, vars):
    for var in vars:
        txt = txt.replace("#VANY#", var, 1)
    return txt
    
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



def processTodaysTasks(tasks, garageMap, nowESTDate, nowESTTime):
    #nowESTDate = "2014-10-22"
    allAdvanceRows = ""
    numAdvanceTasks = 0
    allRows = ""
    numTasks = 0
    hasReturn = False
    for t in tasks:
        if t[2]==HBook.SERVICE_VAULT:
            taskOn = dbDateToEST_String(t[4])
            taskOnDate = taskOn[:10]

            if taskOnDate==nowESTDate:
                taskOnTime = taskOn[11:]
                stdTime = toStdTime(taskOnTime)

                g = garageMap[str(t[11])]
                row = buildVaultTodayRow(g, t, stdTime)
                allRows += row + "\n"
                numTasks=numTasks+1
                if t[3]==2:
                    hasReturn = True
            
        if t[2]==HBook.SERVICE_ADVANCE:
            taskOn = dbDateToEST_String(t[4])
            taskOnDate = taskOn[:10]

            if taskOnDate==nowESTDate:
                taskOnTime = taskOn[11:]
                stdTime = toStdTime(taskOnTime)

                g = garageMap[str(t[11])]
                row = buildAdvanceRow(g, t, stdTime)
                allAdvanceRows += row + "\n"
                numAdvanceTasks=numAdvanceTasks+1
            
    emailTodaysTasksToSupport(nowESTDate,nowESTTime,str(numTasks),allRows,hasReturn,str(numAdvanceTasks),allAdvanceRows,"0","")
    return


def processAdvanceThirtyMins(tasks, garageMap, nowEST, nowESTDate, nowESTTime):
    sNow = str(nowEST)
    sNow = sNow[:16]
    #sNow = "2014-10-22 18:10"
    
    fmt = '%Y-%m-%d %H:%M'
    d1 = datetime.datetime.strptime(sNow, fmt)

    # convert to unix timestamp
    d1_ts = time.mktime(d1.timetuple())

    allRows = ""
    numTasks = 0

    # they are now in seconds, subtract and then divide by 60 to get minutes.
    for t in tasks:
        if t[2]==HBook.SERVICE_ADVANCE:
            taskOn = dbDateToEST_String(t[4])
            d2 = datetime.datetime.strptime(taskOn, fmt)
            d2_ts = time.mktime(d2.timetuple())

            minsAhead =  int(d2_ts-d1_ts) / 60

            print "minutes ahead:  " + str(minsAhead)
            if minsAhead == 30:
                print "--------" + taskOn + " ||||  " + sNow
                print "-------- sending 30 minute reminder to " + str(t)
                taskOnTime = taskOn[11:]
                stdTime = toStdTime(taskOnTime)

                g = garageMap[str(t[11])]
                row = buildAdvanceRow(g, t, stdTime)
                allRows += row + "\n"
                numTasks=numTasks+1
    if numTasks > 0:
        emailAdvanceThirtyMinsTasksToSupport(nowESTDate,nowESTTime,allRows)

    return

def processAdvanceConversion(tasks, nowEST):
    sNow = str(nowEST)
    sNow = sNow[:16]
    #sNow = "2014-10-22 18:10"
    
    fmt = '%Y-%m-%d %H:%M'
    d1 = datetime.datetime.strptime(sNow, fmt)

    # convert to unix timestamp
    d1_ts = time.mktime(d1.timetuple())
    # they are now in seconds, subtract and then divide by 60 to get minutes.
    
    for t in tasks:
        if t[2]==HBook.SERVICE_ADVANCE:
            taskOn = dbDateToEST_String(t[4])
            d2 = datetime.datetime.strptime(taskOn, fmt)
            d2_ts = time.mktime(d2.timetuple())

            minsAhead =  int(d2_ts-d1_ts) / 60
            if minsAhead < 16:
                print "minutes ahead: " + str(minsAhead)
                taskId = t[0]
                personId = t[1]
                lat = t[5]
                lng = t[6]
                carId = t[7]
                print "Advance booking for conversion: taskId,personId,lat,lng,carId" + str(taskId) + "," + str(personId) + ", " + str(lat) + ", " + str(lng) + ", " + str(carId)
                ret = HBook.createBookingFromAdvanceTask(taskId,personId,lat,lng,carId)
                print "Advance booking " + str(taskId) + " converted to Now: " + str(ret)
    return

def emailAdvanceThirtyMinsTasksToSupport(currentDate, asOfTime, allRows):
    templatePath = HCommon.getTemplatePath()
    fp = open(templatePath + 'periodicAdvanceThirtyMins.html', 'r')

    msg = fp.read()
    fp.close()
    
    msg = replaceVariables(msg, (asOfTime, allRows))

    subject = HCommon.formatSubject("ADVANCE to NOW in 15 minutes (as of " + currentDate + " " + asOfTime + ")") 
    HCommon.sendEmail(supportEmail, subject, msg)
    
    return

def buildAdvanceRow(g, t, taskOnTime):
    garageAddress = ""
    garageName = g[1]
    garagePhone = g[4]
    garageAddress = g[5]
    garageLotNum = str(t[14])
    carInfo = str(t[10]) + " " + t[8] + " " + t[9]

    lat = t[5]
    lng = t[6]
    meetupLoc = HBook.getAddressFromLatLng(lat, lng)

    sType = "For Parking"
    if t[3]==2:
        sType = "Bring Car to Customer"

    row = "<tr><td>" +  taskOnTime + "</td><td>" + sType + "</td><td>" + t[13] + " " + str(t[14]) + "</td><td>" + str(t[15]) + "</td><td>" + carInfo + "</td><td>" + str(meetupLoc) + "</td><td>" + garageName + "</td><td>" + str(garagePhone) + "</td><td>" + garageAddress + "</td></tr>"
    
    return row

def processVaultDayReminder(tasks, nextDayDate):
    for t in tasks:
        if t[2]==HBook.SERVICE_VAULT:
            taskOn = dbDateToEST_String(t[4])
            taskOnDate = taskOn[:10]

            if taskOnDate==nextDayDate:
                taskOnTime = taskOn[11:]
                stdTime = toStdTime(taskOnTime)
                lat = t[5]
                lng = t[6]
                meetupLoc = HBook.getAddressFromLatLng(lat, lng)
                email = t[16]
                make = t[8]
                model = t[9]
                color = t[10]
                firstName = t[13]
                taskType = t[3]

                sendVaultDayReminder(email,firstName,taskType,make,model,meetupLoc,stdTime)
    return

def processVaultThreeHoursReminder(tasks, nowEST, nowESTDate):
    sNow = str(nowEST)
    sNow = sNow[:16]
    #sNow = "2014-10-22 18:10"
    
    fmt = '%Y-%m-%d %H:%M'
    d1 = datetime.datetime.strptime(sNow, fmt)

    # convert to unix timestamp
    d1_ts = time.mktime(d1.timetuple())

    # they are now in seconds, subtract and then divide by 60 to get minutes.
    
    for t in tasks:
        if t[2]==HBook.SERVICE_VAULT:
            taskOn = dbDateToEST_String(t[4])
            d2 = datetime.datetime.strptime(taskOn, fmt)
            d2_ts = time.mktime(d2.timetuple())

            minsAhead =  int(d2_ts-d1_ts) / 60

            if minsAhead == 180:
                print "--------" + taskOn + " ||||  " + sNow
                print "-------- sending 3 hour reminder to " + str(t)
                taskOnTime = taskOn[11:]
                stdTime = toStdTime(taskOnTime)
                lat = t[5]
                lng = t[6]
                meetupLoc = HBook.getAddressFromLatLng(lat, lng)
                email = t[16]
                make = t[8]
                model = t[9]
                firstName = t[13]
                taskType = t[3]

                sendVaultThreeHoursReminder(email,firstName,taskType,make,model,meetupLoc,stdTime)

    return

def buildVaultTodayRow(g, t, taskOnTime):
    garageAddress = ""
    garageName = g[1]
    garagePhone = g[4]
    garageAddress = g[5]
    garageLotNum = str(t[14])
    carInfo = str(t[10]) + " " + t[8] + " " + t[9]

    lat = t[5]
    lng = t[6]
    meetupLoc = HBook.getAddressFromLatLng(lat, lng)

    sType = "For Parking"
    if t[3]==2:
        sType = "Bring Car to Customer"

    row = "<tr><td>" +  taskOnTime + "</td><td>" + sType + "</td><td>" + t[13] + " " + str(t[14]) + "</td><td>" + str(t[15]) + "</td><td>" + carInfo + "</td><td>" + str(meetupLoc) + "</td><td>" + garageName + "</td><td>" + str(garagePhone) + "</td><td>" + garageLotNum + "</td><td>" + garageAddress + "</td></tr>"
    
    return row

def processVaultExpired(tasks, garageMap, nowEST, nowESTDate, nowESTTime):
    sNow = str(nowEST)
    sNow = sNow[:16]
    #sNow = "2014-10-22 18:10"
    
    fmt = '%Y-%m-%d %H:%M'
    d1 = datetime.datetime.strptime(sNow, fmt)

    # convert to unix timestamp
    d1_ts = time.mktime(d1.timetuple())

    
    #nowESTDate = "2014-10-22"
    allRows = ""
    numTasks = 0
    hasReturn = False
    #print "processing expired " + str(nowEST) + " , " + nowESTDate
    for t in tasks:
        if t[2]==HBook.SERVICE_VAULT:
            taskOnEST = dbDateToEST(t[4])
            taskOn = dbDateToEST_String(t[4])
            taskOnDate = taskOn[:10]

            if (taskOnEST < nowEST) and (taskOnDate==nowESTDate):
                d2 = datetime.datetime.strptime(taskOn, fmt)
                d2_ts = time.mktime(d2.timetuple())

                minsAhead =  int(d1_ts-d2_ts) / 60

                print "expired minsAhead: " + str(minsAhead)
                if minsAhead < 4:
                    print "--------- " + str(taskOnEST) + " <<<<<<<<<< " +  str(nowEST) + " , "  + taskOnDate + "=========" + nowESTDate
                    taskOnTime = taskOn[11:]
                    stdTime = toStdTime(taskOnTime)
                    g = garageMap[str(t[11])]
                    row = buildVaultTodayRow(g, t, stdTime)
                    allRows += row + "\n"
                    numTasks=numTasks+1
                    if t[3]==2:
                        hasReturn = True
            
    #print allRows
    
    if numTasks > 0:
        emailVaultExpiredTasksToSupport(nowESTDate,nowESTTime,str(numTasks),allRows,hasReturn)
        
    return

def sendVaultDayReminder(email,firstName,taskType,make,model,location,taskTime):
    templatePath = HCommon.getTemplatePath()
    fp = open(templatePath + 'periodicVaultDayCustomerReminder.html', 'r')

    msg = fp.read()
    fp.close()
    
    taskDesc = "meet you to park your " + make + " " + model
    subject = " REMINDER: ValetAnywhere Monthly - Car dropoff tomorrow"
    if taskType == 2:
        taskDesc = "bring your " + make + " " + model + " to you"
        subject = "REMINDER: ValetAnywhere Monthly - Car return tomorrow"
    
    msg = replaceVariables(msg, (firstName,taskDesc,location,taskTime))
    subject = HCommon.formatSubject(subject)
    HCommon.sendEmail(email, subject, msg)

    return

def sendVaultThreeHoursReminder(email,firstName,taskType,make,model,location,taskTime):
    templatePath = HCommon.getTemplatePath()
    fp = open(templatePath + 'periodicVaultThreeHourCustomerReminder.html', 'r')

    msg = fp.read()
    fp.close()
    
    taskDesc = "meet you to park your " + make + " " + model
    subject = " REMINDER: ValetAnywhere Monthly - Car dropoff in 3 hours"
    if taskType == 2:
        taskDesc = "bring your " + make + " " + model + " to you"
        subject = "REMINDER: ValetAnywhere Monthly - Car return in 3 hours"
    
    msg = replaceVariables(msg, (firstName,taskTime,taskDesc,location))

    subject = HCommon.formatSubject(subject)
    HCommon.sendEmail(email, subject, msg)

    return


def emailTodaysTasksToSupport(currentDate, asOfTime, numTasks, allRows,hasReturn,numAdvanceTasks,allAdvanceRows,numAirportTasks,allAirportRows):
    templatePath = HCommon.getTemplatePath()
    fp = open(templatePath + 'periodicDaily.html', 'r')

    msg = fp.read()
    fp.close()
    
    returnText = ""
    if hasReturn == True:
        returnText = "Note that today, there are returns. PLEASE call the garage so they know to get the car out first before our valet arrives."
    
    msg = replaceVariables(msg, (currentDate, asOfTime, numTasks, allRows,returnText,numAdvanceTasks,allAdvanceRows,numAirportTasks,allAirportRows))
    subject = HCommon.formatSubject("Today's Outstanding Scheduled Tasks "+" ("+currentDate+")")
    HCommon.sendEmail(supportEmail, subject, msg)
    return

def emailVaultExpiredTasksToSupport(currentDate, asOfTime, numTasks, allRows,hasReturn):
    templatePath = HCommon.getTemplatePath()
    fp = open(templatePath + 'periodicVaultUrgent.html', 'r')

    msg = fp.read()
    fp.close()
    

    returnText = ""
    if hasReturn == True:
        returnText = "Note that there are returns. PLEASE also call the garage so they know to get the car out first before our valet arrives."

    msg = replaceVariables(msg, (numTasks, allRows, returnText))

    subject = HCommon.formatSubject("URGENT - UNASSIGNED MONTHLY TASK(S) TODAY "+" (as of "+currentDate+ " " + asOfTime +")")
    HCommon.sendEmail(supportEmail, subject, msg)
        
    return



mainProcess()