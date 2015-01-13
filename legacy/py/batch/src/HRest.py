#!/usr/bin/python
# -*- coding: UTF-8 -*-
import tornado.ioloop
import tornado.httpserver
import tornado.web
import json
import HCommon
import HBook
import HValet
import HCustomer
import HAdmin
import sys
import traceback

from time import gmtime, strftime
from tornado.options import define, options, parse_command_line
from tornado import escape
import resource

useSSL = 0;

#resource.setrlimit(resource.RLIMIT_NOFILE, (100000,-1))
define("port", default=9898, help="run on the given port", type=int)

def writeLog(msg):
    tm = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print tm + " - " + msg
    sys.stdout.flush()
    
class RestHandler(tornado.web.RequestHandler):
    #@tornado.web.asynchronous
    def post(self):
        """Post new data to our rest service as a JSON"""
        function=self.get_argument("function", None, True)
        app=self.get_argument("app", None, True)
        
        j = self.json_args
        
        headers = self.request.headers
        referer = ""
        if "Referer" in headers:
            referer = headers["Referer"]
        
        writeLog(app + ", " + function + ": " + str(self.json_args) +  ", " + referer)
        
        ret = {}
        if app=="valet":
            ret = processValet(j, function, headers)
        elif app=="customer":
            ret = processCustomer(j, function, headers)
        elif app=="admin":
            ret = processAdmin(j, function, headers)
        elif app=="web":
            ret = processWeb(j, function, headers)
        elif app=="test":
            ret = j
        

        sRet="Request for " + function + " unsupported"
        if len(ret) > 0:
            sRet = json.dumps(ret)
    
        self.set_header("Content-Type", "text/plain; charset=utf-8")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header('Access-Control-Allow-Headers', 'accept, origin, x-requested-with, x-csrftoken, content-type, email, personId, authToken')
        
        self.set_status(200)
        self.write(sRet)

    def options(self):
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header('Access-Control-Allow-Headers', 'accept, origin, x-requested-with, x-csrftoken, content-type, email, personId, authToken')
        
        self.set_status(200)
        
    def prepare(self):
        try:
            if self.request.headers["Content-Type"].startswith("application/json"):
                self.json_args = json.loads(self.request.body)
            else:
                self.json_args = None
        
        except:
            self.json_args = None
            
    get = post

def processValet(j, function, environ):
    if function=="garageFull.py":
            return HBook.garageFull(j)

    elif function=="readSp.py":
            return HCommon.readSp(j)

    elif function=="readUpdateValetLatestLocation.py":
            return HValet.readUpdateValetLatestLocation(j)

    elif function=="readUpdateValetLatestLocationBg.py":
            return HValet.readUpdateValetLatestLocation(j)

    elif function=="sendCheckoutMessage.py":
            return HBook.sendCheckoutMessage(j)

    elif function=="sendDropOffMessage.py":
            return HCustomer.sendDropOffMessage(j)

    elif function=="sendEmail.py":
            return HBook.sendEmail(j)

    elif function=="updateBookingState.py":
            return HBook.updateBookingState(j)

    elif function=="updateValetProfile.py":
            return HValet.updateValetProfile(j)

    elif function=="updateValetState.py":
            return HValet.updateValetState(j)

    elif function=="updateTicket.py":
            return HValet.updateTicket(j)

    elif function=="valetLogin.py":
            return HValet.valetLogin(j)

    elif function=="validateValetToken.py":
            return HValet.validateValetToken(environ)

    elif function=="readCar.py":
            return HCustomer.readCar(j)
        
    return {}

def processCustomer(j, function, environ):
    if function=="readUpdateLatestLocation.py":
            return HCustomer.readUpdateLatestLocation(j)
    
    elif function=="getPromo.py":
        return HCustomer.getPromo(j)
    
    elif function=="login.py":
            return HCustomer.login(j)

    elif function=="emailResetPwd.py":
            return HCustomer.emailResetPwd(j)
    
    elif function=="readCredits.py":
            return HCustomer.readCredits(j)
        
    elif function=="addCar.py":
            return HCustomer.addCar(j)

    elif function=="deleteCar.py":
            return HCustomer.deleteCar(j)

    elif function=="initiateCheckout.py":
            return HBook.initiateCheckout(j)
            
    elif function=="initiateDropOff.py":
            return HBook.initiateDropOff(j)
            
    elif function=="nearbyFreeValets.py":
            return HValet.nearbyFreeValets(j)

    elif function=="pwdReset.py":
            return HCustomer.pwdReset(j)

    elif function=="readBookingState.py":
            return HBook.readBookingState(j)
    
    elif function=="applyCoupon.py":
            return HBook.applyCoupon(j)

    elif function=="readCars.py":
            return HCustomer.readCars(j)

    elif function=="readCar.py":
            return HCustomer.readCar(j)

    elif function=="readCityBlock.py":
            return HBook.readCityBlock(j)

    elif function=="readPaymentInfo.py":
            return HCustomer.readPaymentInfo(j)

    elif function=="readSp.py":
            return HCommon.readSp(j)

    elif function=="signup.py":
            return HCustomer.signup(j)

    elif function=="submitRating.py":
            return HCustomer.submitRating(j)

    elif function=="updateBookingState.py":
            return HBook.updateBookingState(j)

    elif function=="updateCar.py":
            return HCustomer.updateCar(j)

    elif function=="updatePaymentInfo.py":
            return HCustomer.updatePaymentInfo(j)

    elif function=="updatePreferredCar.py":
            return HCustomer.updatePreferredCar(j)

    elif function=="updateProfile.py":
            return HCustomer.updateProfile(j)

    elif function=="updateRater.py":
            return HValet.updateRater(j)

    elif function=="updateRating.py":
            return HValet.updateRating(j)

    elif function=="validateCustomerToken.py":
            return HCustomer.validateCustomerToken(environ)

    elif function=="viewPersonBookings.py":
            return HBook.viewPersonBookings(j)

    elif function=="checkVerify.py":
            return HCustomer.checkVerify(j)
        
    elif function=="checkPhoneVerification.py":
            return HCustomer.checkVerify(j)
    
    elif function=="updateTrackingCustomer.py":
            return HCustomer.updateTrackingCustomer(j)

    elif function=="validateEmailMobile.py":
            return HCustomer.validateEmailMobile(j)
        
    elif function=="sendDownloadLink.py":
            return HCustomer.sendDownloadLink(j)

    elif function=="scheduleTask" or function=="scheduleTask.py":
            return HBook.scheduleTask(j)
    
    elif function=="scheduleAdvanceTask" or function=="scheduleAdvanceTask.py":
            j["serviceType"] = HBook.SERVICE_ADVANCE
            return HBook.scheduleTask(j)
    
    elif function=="rescheduleAdvanceTask" or function=="rescheduleAdvanceTask.py":
            j["serviceType"] = HBook.SERVICE_ADVANCE
            return HBook.rescheduleTask(j)

    elif function=="cancelAdvanceTask" or function=="cancelAdvanceTask.py":
            j["serviceType"] = HBook.SERVICE_ADVANCE
            return HBook.cancelTask(j)

    elif function=="cancelTask" or function=="cancelTask.py":
            return HBook.cancelTask(j)

    elif function=="scheduleAirportTask" or function=="scheduleAirportTask.py":
            j["serviceType"] = HBook.SERVICE_AIRPORT
            return HBook.scheduleTask(j)
    
    elif function=="rescheduleAirportTask" or function=="rescheduleAirportTask.py":
            j["serviceType"] = HBook.SERVICE_AIRPORT
            return HBook.rescheduleTask(j)
        
    elif function=="scheduleVaultTask" or function=="scheduleVaultTask.py":
            j["serviceType"] = HBook.SERVICE_VAULT
            j["oldFormat"] = 1
            return HBook.scheduleTask(j)
    
    elif function=="rescheduleVaultTask" or function=="rescheduleVaultTask.py":
            j["serviceType"] = HBook.SERVICE_VAULT
            j["oldFormat"] = 1
            return HBook.rescheduleTask(j)
        
    elif function=="signupVault":
            #html5 version
            return HCustomer.signupVaultHtml5(j)        

    elif function=="signupVault.py":
            #native version
            return HCustomer.signupVaultNative(j)        

    elif function=="readVault.py":
            return HBook.readVaultInfo(j)        

    elif function=="vaSignup" or function=="vaSignup.py":
            return HCustomer.vaSignup(j)

    elif function=="readVaultTracking" or function=="readVaultTracking.py":
            return HCustomer.readVaultTracking(j)

    elif function=="submitTip" or function=="submitTip.py":
            return HCustomer.submitTip(j)
        
    elif function=="submitRatingAndTip" or function=="submitRatingAndTip.py":
            return HCustomer.submitRating(j)

    elif function=="readPersonScheduledTasks" or function=="readPersonScheduledTasks.py":
            return HBook.readPersonScheduledTasks(j)

    elif function=="smsSecurityCode" or function=="smsSecurityCode.py":
            return HCustomer.smsSecurityCode(j)
        
    elif function=="validateSecurityCode" or function=="validateSecurityCode.py":
            return HCustomer.validateSecurityCode(j)

    elif function=="readVaultCoverage" or function=="readVaultCoverage.py":
            return HBook.readVaultCoverage(j)

    elif function=="readVaultSignupCoverages" or function=="readVaultSignupCoverages.py":
            return HBook.readVaultSignupCoverages()

    return {}

def processAdmin(j, function, environ):

    if function=="readAdminInfo":
            return HAdmin.readAdminInfo()
    elif function=="clearBookingFromCache.py":
            return HBook.clearBookingFromCache(j)
    elif function=="readSp.py":
            return HCommon.readSp(j)
    elif function=="readCustomer.py":
            return HCustomer.readCustomer(j)
    elif function=="updateBookingState.py":
            return HBook.updateBookingState(j)
    elif function=="login":
            return HAdmin.login(j)
    elif function=="validateToken":
            return HAdmin.validateToken(environ)
    elif function=="addUpdateGarage":
            return HAdmin.addUpdateGarage(j)
    elif function=="deleteGarage":
            return HAdmin.deleteGarage(j)
    elif function=="addUpdateValetEmployee":
            return HAdmin.addUpdateValetEmployee(j)
    elif function=="deleteValetEmployee":
            return HAdmin.deleteValetEmployee(j)
    elif function=="assignValetToVaultTask":
            return HAdmin.assignValetToVaultTask(j)
    elif function=="reassignValetToVaultTask":
            return HAdmin.reassignValetToVaultTask(j)
    elif function=="offlineValet":
            return HValet.offlineValet(j)
    elif function=="reassignValet":
            return HBook.updateValet(j)
    elif function=="applyManualCharge":
            return HBook.applyManualCharge(j)
    elif function=="manualCompleteBooking" or function=="manualCompleteBooking.py":
            return HBook.manualCompleteBooking(j)
    elif function=="cancelTask" or function=="cancelTask.py":
            return HBook.cancelTask(j)
    elif function=="readPersonVaultCharges" or function=="readPersonVaultCharges.py":
            return HCustomer.readPersonVaultCharges(j)
    elif function=="readPersonVaultTaskHistory" or function=="readPersonVaultTaskHistory.py":
            return HCustomer.readPersonVaultTaskHistory(j)
    elif function=="updateVaultSubscription" or function=="updateVaultSubscription.py":
            return HCustomer.updateVaultSubscription(j)
    elif function=="applyVaultCharge":
            return HBook.applyVaultCharge(j)
    elif function=="clearValetBooking":
            return HValet.clearValetBooking(j)
    elif function=="deletePersonBookings":
            return HCustomer.deleteAllCustomerBooking(j)
    elif function=="deleteCustomerVaultSubscription":
            return HCustomer.deleteCustomerVaultSubscription(j)
    elif function=="nukeAccount":
            return HCustomer.deleteAccount(j)
        
        
    return {}

def processWeb(j, function, environ):
    if function=="login.py":
            return HCustomer.login(j)

    elif function=="signup.py":
            return HCustomer.vaultWebSignup(j)
    
    elif function=="apiSignup.py":
            return HCustomer.apiSignup(j)

    elif function=="scheduleVaultTask" or function=="scheduleVaultTask.py":
            j["serviceType"] = HBook.SERVICE_VAULT
            j["oldFormat"] = 1
            return HBook.scheduleTask(j)
    
    elif function=="rescheduleVaultTask" or function=="rescheduleVaultTask.py":
            j["serviceType"] = HBook.SERVICE_VAULT
            j["oldFormat"] = 1
            return HBook.rescheduleTask(j)

    elif function=="readSp.py":
            return HCommon.readSp(j)

    elif function=="validateEmailMobile.py":
            return HCustomer.validateEmailMobile(j)

    elif function=="scheduleAirportBooking" or function=="scheduleAirportBooking.py":
            return HBook.scheduleAirportBooking(j)
    
    elif function=="updatePaymentInfo.py":
            return HCustomer.updatePaymentInfo(j)

    elif function=="sendDownloadLink.py":
            return HCustomer.sendDownloadLink(j)

    elif function=="cancelTask" or function=="cancelTask.py":
            return HBook.cancelTask(j)

    elif function=="emailResetPwd.py":
            return HCustomer.emailResetPwd(j)

    elif function=="addWaitList":
            return HCustomer.addWaitList(j)

    elif function=="readVaultCoverage" or function=="readVaultCoverage.py":
            return HBook.readVaultCoverage(j)
    
writeLog("REST Server starting....")

svr = tornado.httpserver.HTTPServer(tornado.web.Application([
    (r"/rest", RestHandler),
]))

if sys.argv[1]=="1":
    print "usingSSL"
    useSSL = 1;
    svr.bind(8787)
else:
    print "not using SSL"
    svr.bind(8888)


svr.start(0)  # Forks multiple sub-processes

tornado.ioloop.IOLoop.instance().start()
