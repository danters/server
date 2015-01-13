#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HCommon
import HBook
import json
import HValet
import re

rows=HCommon.execProcManyRow("call ReadPersons()",())
for row in rows:
    mobile = row[4]
    
    mobile = re.sub("[^0-9]", "", mobile)
    
    referCode = row[7]
    if len(referCode)==0:
        referNum = mobile[-2:]
        firstName = row[3]
        pattern = re.compile(r'\s+')
        firstName = re.sub(pattern, '', firstName)
        if len(firstName)==0:
            referCode = "DEMO" + referNum
        else:
            referCode = firstName + referNum
        referCode = referCode.lower()
    
    HCommon.updateProc("call UpdatePersonScrub(%s,%s,%s)",(str(row[0]), mobile, referCode))
    print str(row[0]) + ", " + firstName + ", " + mobile + ", " + referCode