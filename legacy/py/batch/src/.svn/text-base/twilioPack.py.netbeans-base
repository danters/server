import HCommon
import pika
import xml.etree.cElementTree as ET
from twilio.rest import TwilioRestClient
from flask import Flask, request, redirect
import twilio.twiml
import sys, traceback

def makeCall(mobileNum):
      try:
            flag=0;

            if("#" in str(mobileNum)):
                    mobileNum=mobileNum.replace('#','')
                    flag=1


            connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
            channel = connection.channel()
            account_sid = "AC71abd04a60cf35d8841c089b38e20ac6"
            auth_token = "9bebbcfc7d6e252e7d3f0519d2bbd098"
            client = TwilioRestClient(account_sid, auth_token)
            root = ET.Element("Response")
            doc = ET.SubElement(root, "Say")
            doc.text="Please check your phone. You have a booking."
            tree = ET.ElementTree(root)
            tree.write("/srv/www/devweb/public_html/phone/dummy.xml")
            call = client.calls.create(to=mobileNum,  # Any phone number
                              from_="+16467982538", # Must be a valid Twilio number
                              url="http://54.191.3.38/phone/dummy.xml",
                              if_machine="Continue"
                              )
            fil_sid=call.sid

            if(flag==0):
                    final=fil_sid+","+mobileNum
                    channel.basic_publish(exchange='',
                          routing_key='callsqueue1',
                          body=str(final))
            if(flag==1):
                    final=fil_sid+","+mobileNum+"#"
                    channel.basic_publish(exchange='',
                          routing_key='callsqueue1',
                          body=str(final))
            return "Success"
      except:
          exc_type, exc_value, exc_traceback = sys.exc_info()
          print HCommon.setError(1,str(exc_value))
          

def sendMessageDropOff(mobileNum,valetName,codeWord):
    try:
        account_sid = "AC71abd04a60cf35d8841c089b38e20ac6"
        auth_token = "9bebbcfc7d6e252e7d3f0519d2bbd098"
        client = TwilioRestClient(account_sid, auth_token)
        valetName=valetName.upper()
        codeWord=codeWord.upper()
        msg="Your Valet "+valetName+" has arrived."+" Handoff code is: "+ codeWord+". Be sure to confirm this code from " + valetName
        message = client.messages.create(to=mobileNum, from_="+16467982538",
                                     body=msg)
        return "Success"
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
	print HCommon.setError(1,str(exc_value))


def sendMessageCheckout(mobileNum,carName,codeWord):
    try:
        account_sid = "AC71abd04a60cf35d8841c089b38e20ac6"
        auth_token = "9bebbcfc7d6e252e7d3f0519d2bbd098"
        client = TwilioRestClient(account_sid, auth_token)
        carName=carName.upper()
        codeWord=codeWord.upper()
        msg="Your "+ carName+" has arrived."+"Your handoff code is: "+ codeWord+". Please say the handoff code to the valet."
        message = client.messages.create(to=mobileNum, from_="+16467982538",
                                     body=msg)
        return "Success"
    except:
        print "Error sending checkout text to " + mobileNum

def cancelBookingCall(mobileNum):
    try:
        mobileNum=str(mobileNum)
        account_sid = "AC71abd04a60cf35d8841c089b38e20ac6"
        auth_token = "9bebbcfc7d6e252e7d3f0519d2bbd098"
        client = TwilioRestClient(account_sid, auth_token)
        call = client.calls.create(to=mobileNum,  # Any phone number
                              from_="+16467982538", # Must be a valid Twilio number
                              url="http://54.191.3.38/phone/cancel.xml",
                              if_machine="Continue"
                              )
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
	print HCommon.setError(1,str(exc_value))
def sendVerifyMessage(mobileNum,msg):
    try:
        account_sid = "AC71abd04a60cf35d8841c089b38e20ac6"
        auth_token = "9bebbcfc7d6e252e7d3f0519d2bbd098"
        client = TwilioRestClient(account_sid, auth_token)
        message = client.messages.create(to=mobileNum, from_="+16467982538",
                                     body=msg)
        return "Success"
    except:
	print HCommon.setError(1,"Invalid Mobile Number")

def sendSms(mobileNum,msg):
    try:
        account_sid = "AC71abd04a60cf35d8841c089b38e20ac6"
        auth_token = "9bebbcfc7d6e252e7d3f0519d2bbd098"
        client = TwilioRestClient(account_sid, auth_token)
        message = client.messages.create(to=mobileNum, from_="+16467982538",
                                     body=msg)
        return "Success"
    except:
	print HCommon.setError(1,"Invalid Mobile Number")


def sendWelcomeLink(mobileNum):
    try:
        account_sid = "AC71abd04a60cf35d8841c089b38e20ac6"
        auth_token = "9bebbcfc7d6e252e7d3f0519d2bbd098"
        client = TwilioRestClient(account_sid, auth_token)
        message = client.messages.create(to=mobileNum, from_="+16467982538",
                                             body="Start using the best on-demand valet service by downloading our app http://val8.me/app")
        return "Success"
    except:
         print HCommon.setError(1,"Invalid Mobile Number")

        
    