#! /usr/bin/python
import HCommon
import HBook
import HCustomer
import json
import sys, traceback

print "Content-Type: text/plain;charset=utf-8"
print

try:
    custInfo=HCommon.execProcManyRow("call ReadCustId()",())
    print custInfo

    for cust in custInfo:
        custBooking=cust[0]
        custPerson=cust[1]
        custCar=cust[2]
        if (custCar!=None):
            carInfo=HCommon.execProcOneRow("call ReadCar(%s)",(str(custCar)))
            if(carInfo[1]!=None):
                carMake=carInfo[0]
                carModel=carInfo[1]
                print carMake
            custInfo=HCommon.execProcOneRow("call ReadCustmerInfo(%s)",(str(custPerson)))
            if(custInfo[0]!=None):
                email=custInfo[0]
                firstName=custInfo[1]
                
                templatePath = HCommon.getTemplatePath()
                fp = open(templatePath + 'cronJob.txt', 'r')
                msg = fp.read()%(firstName,carMake,carModel)
                fp.close()
                print "Sending email!"
                HCommon.sendEmail(email, "ValetAnywhere Alert - IT'S 6:30, PLEASE REQUEST YOUR CAR BACK", msg)
                
except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print HCommon.setError(1,str(exc_value))
        
        
            

    
