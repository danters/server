#!/usr/bin/python
# -*- coding: UTF-8 -*-
import tornado.ioloop
import tornado.web
import tornado.websocket
import json
import HBook
import HValet
import HCustomer
import sys
import traceback

from time import gmtime, strftime
from tornado.options import define, options, parse_command_line
from tornado import escape

define("port", default=8989, help="run on the given port", type=int)

WS_CUSTOMER_LOCATION = 1
WS_BOOK_STATE_CHANGE = 2
WS_VALET_STATE_CHANGE = 3
WS_VALET_ASSIGNMENT = 4
WS_NO_AVAILABLE_VALET = 5
WS_VALET_LOCATION = 6
WS_PERSON_VAULT_CHANGE = 7

useSSL = 0;

# we gonna store clients in dictionary..
customers = dict()
valets = dict()
servers = dict()

def writeLog(msg):
    tm = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print tm + " - " + msg
    sys.stdout.flush()
    return
    
def broadcastValetLocations(origMsg):
    for k in customers:
        cust = customers[k] 
        if cust["needValetLocations"]:
            cust = customers[k]
            cust["object"].write_message(origMsg)
    return

def sendValetLocation(msg):
    cId = msg["customerId"]
    key = str(cId)
    if key in customers:
        cust = customers[key]
        sMsg = json.dumps(msg)
        cust["object"].write_message(sMsg)
    return
        
def sendCustomerLocation(j,msg):
    valetId = j["valetId"]
    key = str(valetId)
    if key in valets:
        valet = valets[key]
        valet["object"].write_message(msg)
        writeLog("sent " + msg + ", to " + key)
    return
		
def sendBookStateToCustomer(bookId):
    booking = HBook.getBooking(bookId)
    key = str(booking["customerPersonId"])
    if key in customers:
        c = customers[key]

        if c is not None:
                ret = {}
                ret["msgType"] = WS_BOOK_STATE_CHANGE
                ret["returnCode"] = 0
                valet = HValet.getValet(booking["valetPersonId"])
                booking["valetAssigned"] = valet
                booking["valet"] = valet
                customer = HCustomer.getCustomer(booking["customerPersonId"])
                if customer is not None:
                    booking['customerLatitude'] = customer["latitude"]
                    booking['customerLongitude'] = customer["longitude"]
                ret["booking"] = booking
                sRet = json.dumps(ret)
                c["object"].write_message(sRet)
                writeLog("sent to customer: " + sRet)
    return
                

def sendVaultStateToCustomer(bookId):
    booking = HBook.getBooking(bookId)
    key = str(booking["customerPersonId"])
    if key in customers:
        c = customers[key]

        if c is not None:
                ret = {}
                ret["msgType"] = WS_BOOK_STATE_CHANGE
                ret["returnCode"] = 0
                valet = HValet.getValet(booking["valetPersonId"])
                booking["valetAssigned"] = valet
                booking["valet"] = valet
                personId = booking["customerPersonId"]
                customer = HCustomer.getCustomer(personId)
                if customer is not None:
                    booking['customerLatitude'] = customer["latitude"]
                    booking['customerLongitude'] = customer["longitude"]
                    
                if booking["state"] == HBook.BOOK_STATE_PARKING_IN_PROGRESS or booking["state"] == HBook.BOOK_STATE_COMPLETED:
                    carId = booking["carId"]
                    sendVaultInfoToCustomer(personId,carId, c)
                    
                ret["booking"] = booking
                sRet = json.dumps(ret)
                c["object"].write_message(sRet)
    return
                
def sendVaultInfoToCustomer(personId, carId, c):
    vault = HBook.getVaultInfo(personId, carId, False)
    ret = {}
    ret["msgType"] = WS_PERSON_VAULT_CHANGE
    ret["returnCode"] = 0
    ret["vault"] = vault
    sRet = json.dumps(ret)
    c["object"].write_message(sRet)
    return

def sendValetAssignmentToCustomer(personId, sBooking):
    key = str(personId)
    if key in customers:
	c = customers[key]
        writeLog("sending to " + str(c))
	if c is not None:
            c["object"].write_message(sBooking)
    return

def sendValetAssignmentToValet(personId, sBooking):
    key = str(personId)
    if key in valets:
	v = valets[key]
	
	if v is not None:
            v["object"].write_message(sBooking)
            writeLog("sent to valet: " + sBooking)
    return

def broadcastValetState(j):
    sMsg = json.dumps(j)	
    writeLog("sending " + sMsg)

    for key in customers:
        cust = customers[key]
        writeLog("sending to " + key + ", " + str(cust["needValetLocations"]))
        if cust["needValetLocations"]:
            cust["object"].write_message(sMsg)
    return

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        print "got the ws1111 call..."
        self.render("index.html")

class ValetHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        self.id = self.get_argument("id")
        self.stream.set_nodelay(True)
        valets[self.id] = {"id": self.id, "object": self}
        writeLog("opened valet " + self.id)

    def on_message(self, message):
    	try:
            writeLog("valet rcvd: " + message)
            j = json.loads(message)
            msgType=j["msgType"]
            if (msgType==WS_VALET_STATE_CHANGE):
                broadcastValetState(j)
            elif (msgType==WS_VALET_LOCATION):
                if "customerId" in j:
                    sendValetLocation(j)
                else:
                    broadcastValetLocations(message)
    	except:        
            exc_type, exc_value, exc_traceback = sys.exc_info()
            writeLog(str(exc_value))
                   
    def on_close(self):
        writeLog("valet closed: " + self.id)
        if self.id in valets:
            del valets[self.id]

class CustomerHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        self.id = self.get_argument("id")
        self.stream.set_nodelay(True)
        customers[self.id] = {"id": self.id, "object": self, "needValetLocations": True}
        writeLog("opened customer " + self.id)

    def on_message(self, message):
    	try:
            writeLog("cust rcvd: " + message)
            j = json.loads(message)
            msgType = j["msgType"]
            if msgType==WS_CUSTOMER_LOCATION:          
                sendCustomerLocation(j, message)
    	except:        
            exc_type, exc_value, exc_traceback = sys.exc_info()
            writeLog(str(exc_value))
#    		print "Customer Error encountered: " + str(exc_value)
       
    def on_close(self):
    	writeLog("closing customer " + self.id)
        if self.id in customers:
            del customers[self.id]

class ServerHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        self.id = self.get_argument("id")
        self.stream.set_nodelay(True)
        servers[self.id] = {"id": self.id, "object": self}
        writeLog("opened server " + self.id) 

    def on_message(self, message):
    	writeLog("svr rcvd: " + str(self.id) + ", " + message)
    	try:
            msg = json.loads(message)
            msgType = msg['msgType']
            if (msgType==WS_VALET_ASSIGNMENT):
                bookingId = msg["bookingId"]
                serviceType = msg["serviceType"]
                booking = None
                booking = HBook.getBooking(bookingId)
                valetId = booking["valetPersonId"]
                customerId = booking["customerPersonId"]
                valet = HValet.getValet(valetId)
                ret = {}
                ret["returnCode"] = 0
                ret["msgType"] = WS_VALET_ASSIGNMENT
                ret["valetAssigned"] = valet
                ret["valet"] = valet
                booking["valetAssigned"] = valet
                booking["valet"] = valet
                customer = HCustomer.getCustomer(customerId)
                if customer is not None:
                    booking['customerLatitude'] = customer["latitude"]
                    booking['customerLongitude'] = customer["longitude"]
                ret["booking"] = booking
                sBooking = json.dumps(ret)

                sendValetAssignmentToCustomer(customerId, sBooking)
                ret["customer"] = customer
                ret["car"] = HCustomer.getCarInfo(booking["carId"])
                sBooking = json.dumps(ret)
                sendValetAssignmentToValet(valetId, sBooking)
                
            elif (msgType==WS_BOOK_STATE_CHANGE):
                bookingId = msg["bookingId"]
                serviceType = msg["serviceType"]
                if serviceType==HBook.SERVICE_VAULT:
                    sendVaultStateToCustomer(bookingId)
                else:
                    sendBookStateToCustomer(bookingId)

    	except:        
            exc_type, exc_value, exc_traceback = sys.exc_info()
            writeLog("Server ERROR encountered: " + str(exc_value))
       
    def on_close(self):
    	writeLog("closing server " + self.id)
        if self.id in servers:
            del servers[self.id]

            
writeLog("Websocket Server starting....")

app = tornado.web.Application([
    (r'/v', ValetHandler),
    (r'/c', CustomerHandler),
    (r'/s', ServerHandler),
])

if __name__ == '__main__':
    if sys.argv[1]=="1":
        print "usingSSL"
        useSSL = 1;
        app.listen(8686)
    else:
        print "not using SSL"
        app.listen(options.port)
        
#    app.listen(8989, address='localhost')
    tornado.ioloop.IOLoop.instance().start()            