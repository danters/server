#!/usr/bin/python
# -*- coding: UTF-8 -*-
import pika
import HCommon
import HValet
import HBook
import json
import twilioPack
import sys, traceback

from tornado.ioloop import IOLoop
from tornado import gen
from tornado.websocket import websocket_connect
from time import gmtime, strftime

client = None

useSSL = 0;

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='bookingQ')

print ' [*] Waiting for messages. To exit press CTRL+C'

def writeLog(msg):
    tm = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print tm + " - " + msg
    sys.stdout.flush()

def processMessage(ch, method, properties, body):
    writeLog("rcvd: " + body)
    j = json.loads(body)

    msgType=j["msgType"]
    wsMsg = {}
    try:
        if (msgType==HCommon.MSG_ASSIGN_DROPOFF):
            if "serviceType" in j and j["serviceType"]==3:
                wsMsg["bookingId"] = j["bookingId"]
                wsMsg["serviceType"] = 3
                wsMsg["msgType"] = HCommon.WS_VALET_ASSIGNMENT
                writeToWebSocket(wsMsg)
                valetMobile = str(j["valetMobile"])
                callPhone(valetMobile)
            else:
                assignCheckinValet(j)
                
        elif (msgType==HCommon.MSG_ASSIGN_CHECKOUT):
            if "serviceType" in j and j["serviceType"]==3:
                wsMsg["bookingId"] = j["bookingId"]
                wsMsg["serviceType"] = 3
                wsMsg["msgType"] = HCommon.WS_VALET_ASSIGNMENT
                writeToWebSocket(wsMsg)
                valetMobile = str(j["valetMobile"])
                callPhone(valetMobile)
            else:
                assignCheckoutValet(j)    
                
        elif (msgType==HCommon.MSG_BOOK_STATE_UPDATE):
            bookingId=j["bookingId"]
            wsMsg["bookingId"] = bookingId
            wsMsg["serviceType"] = j["serviceType"]
            wsMsg["msgType"] = HCommon.WS_BOOK_STATE_CHANGE
            if "valetMobile" in j:
                valetMobile=j["valetMobile"]
                #twilioPack.cancelBookingCall(valetMobile)
            
            writeToWebSocket(wsMsg)
        elif (msgType==HCommon.MSG_VALET_STATE_UPDATE):
            bookingId=j["bookingId"]
            wsMsg["personId"] = j["personId"]
            wsMsg["state"] = j["state"]
            wsMsg["serviceType"] = j["serviceType"]
            wsMsg["msgType"] = HCommon.WS_VALET_STATE_CHANGE
            writeToWebSocket(wsMsg)
        elif (msgType==HCommon.MSG_CUSTOMER_LOC_UPDATE):
            j["msgType"] = HCommon.WS_CUSTOMER_LOCATION
            writeToWebSocket(j)
        elif (msgType==HCommon.MSG_VALET_LOC_UPDATE):
            j["msgType"] = HCommon.WS_VALET_LOCATION
            writeToWebSocket(j)
    except:
	exc_type, exc_value, exc_traceback = sys.exc_info()
        writeLog("Error: " + str(exc_value))
	

def assignCheckinValet(j):
    wsMsg = {}
    bookingId=j["bookingId"]
    cityBlockId=j["cityBlockId"]
    serviceType=j["serviceType"]
    writeLog("dropoff assigning to booking " + str(bookingId) + ", cityBlock " + str(cityBlockId))
    wsMsg["bookingId"] = bookingId
    wsMsg["serviceType"] = serviceType
    wsMsg["msgType"] = HCommon.WS_VALET_ASSIGNMENT
    booking=HBook.getBooking(bookingId)

    if serviceType==HBook.SERVICE_NOW:
        valet = None
        valet = HBook.assignBestAvailableValet(bookingId,False,cityBlockId)
        if(valet is None):
            booking['state']=HBook.BOOK_STATE_NOVALETDROPOFF
            bookingText = json.dumps(booking)
            HBook.setBooking(bookingId, bookingText)
            wsMsg["msgType"] = HCommon.WS_NO_AVAILABLE_VALET
            writeLog("No available valet for dropoff assignment of bookingId " + str(bookingId))
        else:
            sValet = json.dumps(valet)
            phoneNum=str(valet['mobile'])
            callPhone(phoneNum)

            writeLog("Valet Assigned: " + sValet)
    else:
        valetId = booking['valetPersonId']
        valet = HValet.getValet(valetId)
        sValet = json.dumps(valet)
        phoneNum=str(valet['mobile'])
        callPhone(phoneNum)
        writeLog("Valet Assigned: " + sValet)

    writeToWebSocket(wsMsg)

def assignCheckoutValet(j):
    wsMsg = {}
    bookingId=j["bookingId"]
    serviceType=j["serviceType"]
    wsMsg["bookingId"] = bookingId
    wsMsg["serviceType"] = serviceType
    wsMsg["msgType"] = HCommon.WS_VALET_ASSIGNMENT
    
    writeLog("checkout assigning to booking " + str(bookingId))
    
    if serviceType==HBook.SERVICE_NOW:
        valet = HBook.assignBestAvailableValet(bookingId,True,None)
        if(valet is None):
            writeLog("No available valet for checkout assignment")
        else:
            sValet = json.dumps(valet)
            phoneNum=str(valet['mobile'])
            wsMsg["valetId"] = valet["personId"]
            callPhone(phoneNum)
            writeLog("Valet Assigned: " + sValet)
    else:
        booking=HBook.getBooking(bookingId)
        valetId = booking['valetPersonId']
        valet = HValet.getValet(valetId)
        sValet = json.dumps(valet)
        phoneNum=str(valet['mobile'])
        wsMsg["valetId"] = valet["personId"]
        callPhone(phoneNum)
        writeLog("Valet Assigned: " + sValet)
        
    writeToWebSocket(wsMsg)


def callPhone_old(phoneNum):
    return

def callPhone(phoneNum):
    if HCommon.isDev()==True:
        return
    try:
        ret= twilioPack.makeCall(phoneNum)
    except:        
        exc_type, exc_value, exc_traceback = sys.exc_info()
#    		print "Customer Error encountered: " + str(exc_value)
    
    
@gen.coroutine
def startWebSocket():
    writeLog("thread started")
    global client
    wsHost = HCommon.getWebSocketServerHost(useSSL)
    writeLog("opening server " + wsHost)
#    client = yield websocket_connect("ws://localhost:8989/s?id=111")
    client = yield websocket_connect(wsHost)
    writeLog("websocket server " + wsHost + " opened")

def writeToWebSocket(j):
    msg = json.dumps(j)
    client.write_message(msg)

writeLog("Message Queue starting...")
if sys.argv[1]=="1":
    print "usingSSL"
    useSSL = 1;
else:
    print "not using SSL"


IOLoop.current().run_sync(startWebSocket)

channel.basic_consume(processMessage,
                      queue='bookingQ',
                      no_ack=True)

channel.start_consuming()