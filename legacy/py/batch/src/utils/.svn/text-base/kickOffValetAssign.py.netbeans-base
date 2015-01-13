#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HCommon
import HBook

msg = {}
msg["bookingId"] = 1
msg["cityBlockId"] = 7
msg["serviceType"] = HBook.SERVICE_NOW
HBook.sendToMessageQueue(msg, HCommon.MSG_ASSIGN_DROPOFF)
        
