#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import AWSEmail
import HCommon

email='support@valetanywhere.com'
customerName = "Dante"
pickupLocation = "399 Park Ave"
pickupTime = "Oct 30, 2014 10:00AM"
monthlyPrice = "325.00"
billDay = "18"
templatePath = HCommon.getTemplatePath()
#fp = open(templatePath + 'signupVaultWelcome.txt', 'r')
fp = open(templatePath + 'signupSHVaultWelcome.txt', 'r')

#msg = fp.read()%(customerName,pickupLocation,pickupTime,monthlyPrice,billDay)
msg = fp.read()%(customerName,pickupLocation,pickupTime)
AWSEmail.sendemail(email, "DEV - ValetAnywhere Vault First Parking", msg)
