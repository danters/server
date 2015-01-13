#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HCommon
import HBook
import HCustomer
import HValet
import json

f = open("testResult.txt","w")
f.write("Content-Type: text/plain;charset=utf-8\n")

f.write("\n==========\n==========\n")
f.write("\nEnvironment: " + HCommon.ENV + ", isDev=" + str(HCommon.isDev()))
for i in range(100,500):
	booking = HBook.getBooking(i)
	if booking != None:
		f.write("\n=========================================================\n\n")
		f.write("Booking number : "+str(i)+" -----\n")
		f.write(json.dumps(booking)+"\n\n")

f.write("\n==========\n==========\n")
for i in range(0,300):
	valet = HValet.getValet(i)
	if valet != None:
		f.write("\n=========================================================\n\n")
		f.write("Valet number : "+str(i)+" -----\n")
		f.write(json.dumps(valet)+'\n\n')

f.write("\n==========\n==========\n")
for i in range(200,600):
	customer = HCustomer.getCustomer(i)
	if customer != None:
		f.write("\n=========================================================\n\n")
		f.write("Customer number : "+str(i)+" -----\n")
		f.write(json.dumps(customer)+'\n\n')
